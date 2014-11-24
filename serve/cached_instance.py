"""
decorator to make functions that only ever return the first non-false value they create
"""
from datetime import datetime, timedelta
import time

class CachedInstance(object):
  "a decorator"
  def __init__(self, timeout=0, file=''):
    "timeout: int seconds	file='string path to store result'"
    self.result = {}
    self.timeouts = {}
    self.time = datetime.now()
    self.timeout = timeout
    self.file = file

  def __call__(self, fn):
    "wrap our function"
    def wrapper(*a, **k):
      uid = a[0].uid
      # regenerate content on finding a recache parameter
      if k.get('recache', 0):
        self.result[uid] = ''
	del k['recache']
      if self.timedout(uid):
        self.result[uid] = ''
      # regenerate if no content available
      if not self.result.get(uid, ''):
        self.result[uid] = fn(*a, **k) 
        self.timeouts[uid] = datetime.now()
	if self.file:
	  open(self.file % uid, 'w').write(self.result[uid])
      return self.result[uid]
    return wrapper

  def timedout(self, uid):
    "returns True if we have timed out"
    # if there's no timeout we will not regenerate
    if not self.timeout:
      return False
    if not self.timeouts.get(uid):
      return False
    return datetime.now() >= self.timeouts[uid] + timedelta(seconds=self.timeout)

def cached_instance(fn):
  return CachedInstance()(fn)

if __name__=='__main__':
  class X(object):
    def __init__(self, uid):
      self.uid = uid
  
    @cached_instance
    def fn(self):
      return datetime.now()

    @CachedInstance(timeout=1)
    def fn2(self):
      return datetime.now()

    @CachedInstance(file='/tmp/test_%d.html')
    def fn3(self):
      return `datetime.now()`      

  xs = [X(i) for i in range(3)]
  t1s = [x.fn() for x in xs]
  print t1s
  #assert list(set(t1s))==xs, 'each instance should have an unique value'
  t2s = [x.fn() for x in xs]
  assert t1s==t2s, 'should return cached values'  
  t3s = [x.fn() for x in xs]
  assert t1s==t3s, 'should return cached values'  
  t4s = [x.fn(recache=True) for x in xs]
  assert t1s!=t4s, 'should return new values'  

  t5s = [x.fn2() for x in xs]
  t6s = [x.fn2() for x in xs]
  assert t5s==t6s, "values should be cached"
  time.sleep(2)
  t7s = [x.fn2() for x in xs]
  assert t5s!=t7s, "values should refreshed"

  t8s = [x.fn3() for x in xs]
  t9s = [open('/tmp/test_%d.html' % x.uid).read() for x in xs] 
  assert t8s==t9s, "should have been copied to file"

