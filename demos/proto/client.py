import sys
import xmlrpclib

proxy = xmlrpclib.ServerProxy("http://localhost:8000/")

res = proxy.get_article(sys.argv[1])
print res
