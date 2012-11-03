import sys
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer
from MySQLdb import *
from MySQLdb.cursors import DictCursor

def get_article(id):
    try:
        db = connect('localhost','demo','demo',db='demo', cursorclass=DictCursor)
        c = db.cursor()
        c.execute('SELECT * FROM demo WHERE id=%s'%id)
        res = c.fetchall()
        if c.rowcount==1:
            return str(res[0])
        else:
            return ''
        db.close()
    except Exception,e:
        print e
        print 'Erreur inconnue'
        return ''

server = SimpleXMLRPCServer(("localhost", 8000))
print "Listening on port 8000..."
server.register_function(get_article, "get_article")
server.serve_forever()

