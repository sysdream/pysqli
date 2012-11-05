#-*- coding: utf-8 -*-

from injector import GetInjector, PostInjector, CookieInjector, \
    UserAgentInjector, CmdInjector
from context import Context
from exceptions import OutboundException, PluginMustOverride, Unavailable
from async import AsyncPool
from wrappers import DatabaseWrapper, TableWrapper, FieldWrapper
from types import IntType, StringType

DBS_ENUM = 0x01
TABLES_ENUM = 0x02
COLS_ENUM = 0x04
FIELDS_ENUM = 0x08
STR = 0x10
COMMENT = 0x20

class DBMSFactory:
    """
    DBMS factory.
    
    Set up a DBMS plugin with a specific injector.
    """
    
    def __init__(self, plugin_class, name, desc):
        self._clazz = plugin_class
        self._name = name
        self._desc = desc

    def get(self, context=Context(), limit_max_count=500):
        """
        Factor a GetInjector and set up the plugin
        """
        inst = self._clazz(GetInjector(context), limit_max_count)
        inst.name = self._name
        inst.desc = self._desc
        return inst

    def post(self, context=Context(), limit_max_count=500):
        """
        Factor a PostInjector and set up the plugin
        """
        inst = self._clazz(PostInjector(context), limit_max_count)
        inst.name = self._name
        inst.desc = self._desc
        return inst
        
    def user_agent(self, method, context=Context(), limit_max_count=500):
        """
        Factor a UserAgentInjector and set up the plugin
        """
        inst = self._clazz(UserAgentInjector(method, context), limit_max_count)
        inst.name = self._name
        inst.desc = self._desc
        return inst

    def cookie(self, method='GET', context=Context(), limit_max_count=500, data=None, content_type=None):
        """
        Factor a CookieInjector and set up the plugin
        """
        inst = self._clazz(CookieInjector(method, context, data, content_type), limit_max_count)
        inst.name = self._name
        inst.desc = self._desc
        return inst

    def cmd(self, context=Context(), limit_max_count=500):
        """
        Factor a CmdInjector and set up the plugin
        """
        inst = self._clazz(CmdInjector(context), limit_max_count)
        inst.name = self._name
        inst.desc = self._desc
        return inst    
     
    def custom(self, injector, *args, **kwargs):
        """
        Factor a custom injector and set up the plugin
        """
        if 'limit_max_count' in kwargs:
            limit_max_count = kwargs['limit_max_count']
            del kwargs['limit_max_count']
        else:
            limit_max_count = 500
        inst = self._clazz(injector(*args, **kwargs), limit_max_count)
        inst.name = self._name
        inst.desc = self._desc
        return inst

class dbms:

    """
    Class decorator for DBMS

    Use it to declare a class as a DBMS plugin. 
    """

    def __init__(self, name, desc):
        """
        Constructor.
        
        name: dbms name
        desc: dbms description
        """
        self.name = name
        self.desc = desc

    def __call__(self, inst):
        return DBMSFactory(inst, self.name, self.desc)


class allow:

    """
    Plugin decorator
    
    Set the plugin capabilities.
    """
   

    def __init__(self, flags):
        self.flags = flags

    def __call__(self, inst):
        def wrapped_(*args):
            a = inst(*args)
            if hasattr(a,'capabilities'):
                a.capabilities |= self.flags
            else:
                a.capabilities = self.flags
            return a
        return wrapped_


class DBMS:
    """
    DBMS default class

    This class implements an abstraction of the underlying DBMS. It
    provides methods to perform databases and tables enumeraton as
    well as data extraction.

    This abstraction allows the user to focus on the data he wants
    to get rather than the injected code.

    """

    def __init__(self, forge, injector=None, limit_count_max=500):
        """
        Constructor.
        
        forge: forge class to use
        injector: injector instance to use
        limit_count_max: maximum number of records
        """
        self.forge_class = forge
        self.context = injector.get_context()
        self.forge = forge(self.context)
        self.injector = injector
        self.limit_count_max = limit_count_max        
        self.current_db = None
        self.current_user = None


    def has_cap(self, cap):
        """
        Determine if the plugin has a given capability.
        
        Capability must be part of [DBS_ENUM, TABLES_ENUM, COLS_ENUM,
        FIELDS_ENUM, STR, COMMENT]
        """
        return (self.capabilities&cap)==cap

    def determine(self):
        """
        This method must return True if the DBMS can be determined, False otherwise.
        """
        raise PluginMustOverride

    def get_forge(self):
        """
        Retrieve the forge instance
        """
        return self.forge


    def set_injector(self, injector):
        """
        Set injector.
        
        injector: instance of AbstractInjector or its derivated classes.
        """
        method = self.injector.getMethod()
        self.injector = injector(self.context, method)

    def  get_injector(self):
        """
        Retrieve the injector
        """
        return self.injector

    def set_forge(self, forge):
        """
        Set SQL forge.
        
        forge: SQL forge to use.
        """
        self.forge_class = forge
        self.forge = forge(self.context)


    def set_trigger(self, trigger):
        """
        Set injector's default trigger

        trigger: the new trigger to use
        """
        self.injector.set_trigger(trigger)


    def use(self, db):
        """
        Select a database.
        
        db: database name (string)
        """
        self.current_db = db
        return DatabaseWrapper(self, self.current_db)

    def apply_bisec(self,cdt,min,max):
        """
        Use SQL bisection to determine an integer value. 
        """
        while (max-min)>1:
            mid = (max-min)/2 + min
            if self.injector.inject(self.forge.wrap_bisec(self.forge.forge_cdt(cdt,mid))):
                max = mid
            else:
                min = mid
        return min


    def get_inband_str(self, sql):
        """
        Extract a string through inband SQL injection
        """
        return self.injector.inject(self.forge.wrap_sql(self.forge.forge_second_query(sql)))


    def get_inband_int(self, sql):
        """
        Extract an integer through inband SQL injection
        """
        return int(self.get_inband_str(sql))

    def get_blind_int(self, sql):
        """
        Extract an integer through blind SQL injection
        """
        pool = AsyncPool(self)
        if self.context.is_multithread():
            pool.add_bisec_task(sql, 0, self.limit_count_max)
        else:
            pool.add_classic_bisec_task(sql, 0, self.limit_count_max)
        pool.solve_tasks()
        return pool.result[0]
            

    def get_char(self, sql, pos):
        """
        Forge SQL to extract a character at a given position
        """
        return self.forge.get_char(sql, pos)
        
    def get_blind_str(self, sql):
        """
        Extract a string through a blind SQL injection
        """
        size = self.get_blind_int(self.forge.string_len(sql))
        if size==(self.limit_count_max-1):
            raise OutboundException()
        if self.context.is_multithread():
            pool = AsyncPool(self)
            for p in range(size):
                pool.add_bisec_task(self.forge.ascii(self.forge.get_char(sql,p+1)),0,255)
            pool.solve_tasks()
            return pool.get_str_result()
        else:
            result = ''
            for p in range(size):
                pool = AsyncPool(self)
                pool.add_classic_bisec_task(self.forge.ascii(self.forge.get_char(sql, p+1)), 0, 255)
                pool.solve_tasks()
                result += pool.get_str_result()
            return result

    def get_int(self, sql):
        """
        Extract an integer.
        
        Supports inband and blind SQL injection. 
        """
        if self.context.is_blind():
            return self.get_blind_int(sql)
        else:
            return self.get_inband_int(sql)

    def get_str(self, sql):
        """
        Extracts a string.
        
        Supports inband and blind SQL injection.
        """
        if self.context.is_blind():
            return self.get_blind_str(sql)
        else:
            return self.get_inband_str(sql)

    def version(self):
        """
        Retrieve the DBMS version string.
        """
        return self.get_str(self.forge.get_version())

    def database(self, db=None):
        """
        Retrieve an instance of DatabaseWrapper.
        
        If db is specified, retrieve the specified database. If not,
        retrieve the current database.
        """
        if db is not None:
            return DatabaseWrapper(self, db)
        else:
            self.current_db = self.get_str(self.forge.get_current_database())
            return DatabaseWrapper(self, self.current_db)

    def get_nb_databases(self):
        """
        Retrieve the number of databases.
        """
        return self.get_int(self.forge.get_nb_databases())

    def get_database_name(self, id):
        """
        Retrieve the database name.
        
        id: index of the database's name (0<id<count)
        """
        return self.get_str(self.forge.get_database_name(id))

    def databases(self):
        """
        Enumerates all existing/accessible databases
        """
        if self.has_cap(DBS_ENUM):
            n = self.get_nb_databases()
            for i in range(n):
                yield DatabaseWrapper(self,self.get_database_name(i))
        else:
            raise Unavailable()


    def get_nb_tables(self,db=None):
        """
        Retrieve the number of tables belonging to a database. If no database
        is specified, use the current database.
        
        db: target database (default: None)
        """
        if db:
            return self.get_int(self.forge.get_nb_tables(db=db))
        else:
            db = self.database()
            return self.get_int(self.forge.get_nb_tables(db=db))

    def get_table_name(self, id,db=None):
        """
        Retrieve a given table's name from a specified DB.
        """
        return self.get_str(self.forge.get_table_name(id,db=db))
    
    def tables(self, db=None):
        """
        Enumerates all tables fro a given database. If not specified, use the
        current database.
        """
        if self.has_cap(TABLES_ENUM):
            # if db not given, then find the db
            if db is None:
                if self.current_db is None:
                    self.database()
                db = self.current_db

            n = self.get_nb_tables(db)
            for i in range(n):
                yield TableWrapper(self, self.get_table_name(i, db), db)    
        else:
            raise Unavailable()

    def get_nb_fields(self, table,db):
        """
        Retrieve the number of fields (columns) from a given table and database.
        """
        return self.get_int(self.forge.get_nb_fields(table, db=db))

    def get_field_name(self, table, id, db):
        """
        Retrieve a given field's name from a given table and database
        """
        return self.get_str(self.forge.get_field_name(table, id, db))

    def fields(self, table, db=None):
        """
        Enumerates all fields from a given table. If a database is specified,
        use it. 
        """
        if self.has_cap(FIELDS_ENUM):
            if db is None:
                if self.current_db is None:
                    self.database()
                db = self.current_db
            n = self.get_nb_fields(table, db)
            for i in range(n):
                yield FieldWrapper(self, table, db, self.get_field_name(table, i, db))
        else:
            raise Unavailable()


    def user(self):
        """
        Retrieve the current DB user.
        """
        return self.get_str(self.forge.get_user())

    def count_table_records(self, table, db=None, max=1000000):
        """
        Count the number of records of a given table. If db is specified, use
        the corresponding database.
        """
        if db is None:
            if self.currrent_db is None:
                self.database()
            db = self.current_db
        return self.get_int(self.forge.count(self.forge.select_all(table, db)))


    def get_record_field_value(self, field, table, pos, db=None):
        """
        Get a record's field value. 
        
        field: field name
        table: table name
        db: database name (default: current DB)
        pos: record index
        """
        if db is None:
            if self.currrent_db is None:
                self.database()
            db = self.current_db
        return self.get_str(self.forge.get_table_field_record(field,table, db, pos))

    def __getitem__(self, i):
        """
        Allows the plugin to act as a dictionary.
        
        i: database index or name.
        """
        if type(i) is IntType:
            d = self.getDatabaseName(i)
            if d is None:
                raise IndexError
            else:
                return DatabaseWrapper(self, d)
        elif type(i) is StringType:
            return DatabaseWrapper(self, i)



    def __len__(self):
        """
        Return the number of databases.
        """
        return self.get_nb_databases()

