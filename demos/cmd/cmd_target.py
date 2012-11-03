import sys
from MySQLdb import *
from MySQLdb.cursors import DictCursor

try:
    db = connect('localhost','demo','demo',db='demo', cursorclass=DictCursor)
    c = db.cursor()
    c.execute('SELECT * FROM demo WHERE id=%s'%sys.argv[1])
    res = c.fetchall()
    if c.rowcount==1:
        print res[0]
        sys.exit(0)
    else:
        print 'Article inexistant'
        sys.exit(2)
    db.close()
except Exception,e:
    print e
    print 'Erreur inconnue'
    sys.exit(3)
