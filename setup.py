from distutils.core import setup

setup(	name="PySQLi",
	version="1.0",
	description="Python SQL injection framework",
	author="Damien Cauquil",
	author_email="d.cauquil@sysdream.com",
	url="http://www.sysdream.com",
	packages=[
		'pysqli',
		'pysqli.core',
		'pysqli.dbms'],
	long_description="PySQLi is an SQL inection framework allowing exploit development and complex exploitations."
)
