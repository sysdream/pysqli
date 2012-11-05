#-*- coding:utf-8 -*-

from ..core.dbms import *
from ..core.forge import SQLForge

class Mysql4Forge(SQLForge):
	def __init__(self, context):
		SQLForge.__init__(self, context)
		
	"""
	Define overrides
	"""
	
	def get_version(self):
		return "@@VERSION"
		
	def wrap_bisec(self, cdt):
		return self.wrap_sql("SELECT IF(%s,%s,(SELECT %s UNION ALL SELECT %s ))" % (cdt,self.wrap_field('0'),self.wrap_field('0'),self.wrap_field('0')))


@dbms('mysqlv4','Mysql version 4')
@allow(COMMENT | STR)
class Mysql4(DBMS):	

	def __init__(self, injector, limit_count_max=500):
		DBMS.__init__(self, Mysql4Forge, injector, limit_count_max)
