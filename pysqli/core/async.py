#-*- coding:utf-8 -*-

"""
This module handles every asynchronous request.

Classes:
    OptimizedAsyncBisecInjector
    AsyncBisecInjector
    AsyncInjector
    AsyncPool
"""

from threading import Thread

class OptimizedAsyncBisecInjector(Thread):
    """ Optimized asynchronous bisection-based injector
        
    This injector uses an improved bisection to speed up the
    injection.

    The main idea behind this improved method is simple:
    using Python's multithreading, 3 parallelized requests take approx.
    the same time to run than 2 requests (statistically). This can be
    used to speed up the classic bisection approach by not testing a single
    value but 3 at a time. Given the results, the search interval is divided.
    by 4 instead of 2. 12 requests are required instead of 8 to complete the
    search, the same as 6 successive requests instead of 8. 
    """

    def __init__(self, db, cdt, min, max):
        Thread.__init__(self)
        self.db = db
        self.result = None
        self.min = min
        self.max = max
        self.cdt = cdt
        self.pool = AsyncPool(self.db)
        
    
    def run(self):
        while (self.max-self.min)>1:
            # create another async pool
            self.pool.clear_tasks()
              
            # compute the 3 mids
            mid = (self.max-self.min)/2 + self.min
            mid_l = (mid-self.min)/2 + self.min
            mid_r = (self.max-mid)/2 + mid
              
            self.pool.add_task(self.db.forge.wrap_bisec(self.db.forge.forge_cdt(self.cdt,mid)))
            self.pool.add_task(self.db.forge.wrap_bisec(self.db.forge.forge_cdt(self.cdt,mid_l)))
            self.pool.add_task(self.db.forge.wrap_bisec(self.db.forge.forge_cdt(self.cdt,mid_r)))
             
            self.pool.solve_tasks()
    
            if (self.pool.result[0]==False):
                if (self.pool.result[2]==False):
                    self.min = mid_r
                else:
                    self.min = mid
                    self.max = mid_r
            else:
                if (self.pool.result[1]==False):
                    self.min = mid_l
                    self.max = mid
                else:
                    self.max = mid_l
        self.result = self.min


class AsyncBisecInjector(Thread):
    """
    Classic asynchronous bisection injector
    """
    
    def __init__(self, db, cdt, min, max):
        Thread.__init__(self)
        self.db = db
        self.result = None
        self.min = min
        self.max = max
        self.cdt = cdt

    def run(self):
        while (self.max-self.min)>1:
            mid = (self.max-self.min)/2 + self.min
            if self.db.injector.inject(self.db.forge.wrap_bisec(self.db.forge.forge_cdt(self.cdt,mid))):
                self.max = mid
            else:
                self.min = mid
        self.result = self.min


class AsyncInjector(Thread):
    
    """
    Asynchronous wrapper
    """

    def __init__(self, db, sql):
        Thread.__init__(self)
        self.db = db
        self.sql = sql
        self.result = None
        self.error = False

    def run(self):
        try:
            self.result = self.db.injector.inject(self.sql)
        except Exception, e:
            print e
            raise 'oops'
            self.error = True


class AsyncPool:
    
    """
    Pool of asynchronous tasks.
    
    This class handles a set of requests, send them through the injector and
    group the results.
    """

    def __init__(self, db,limit=5):
        self.db = db
        self.limit = limit
        self.clear_tasks()
    
    
    def add_bisec_task(self, cdt, min, max):
        """
        Enqueue a bisection task to the pool
        """
        self.tasks.append(OptimizedAsyncBisecInjector(self.db, cdt, min, max))

    def add_classic_bisec_task(self, cdt, min, max):
        """
        Enqueue a 'classic' bisection injection
        """
        self.tasks.append(AsyncBisecInjector(self.db, cdt, min, max))
    
    def add_task(self, sql):
        """
        Enqueue a basic task 
        """
        self.tasks.append(AsyncInjector(self.db,sql))

    def clear_tasks(self):
        """
        Clear all tasks
        """
        self.tasks = []
        self.result = []

    def solve_tasks(self):
        """
        Launch all tasks and grab results
        """
        done = 0
        stop = 0
        for task in self.tasks:
            stop+=1
            try:
                task.start()
                if stop==self.limit:
                    for t in range(stop):
                        task = self.tasks[t+done]
                        task.join()
                        self.result.append(task.result)
                        del task
                    done += stop
                    stop=0
            except Exception:
                print 'Unable to launch thread #%d' % (stop+done)

        if stop>0:
            for t in range(stop):
                task = self.tasks[t+done]
                task.join()
                self.result.append(task.result)
                del task
                            
    def get_str_result(self):
        """
        Pack the result as a string
        """
        res = ''
        for r in self.result:
            res += '%c' % r
        return res
 
