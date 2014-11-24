"""
This module implements the FLOAT class, used (sparingly please!) for real number storage and manipulation.

For efficiency, and amaximum robustness, the .value property should be used explicitly for any numerical manipulation, though arithmetic expressions are supported.

(Ian Howie Mackenzie - April 2009)
"""

class FLOAT(object):
  """
  simple float handling
  """

  def __init__(self,var=0):
    """
    create our float
    """
    self.valid=True
    try:
      self.value=float(var)
    except:
      self.value=0
      self.valid=False
      
  def sql(self, quoted=True):
    """ gives sql string format, including quotes (why not..)
    """
    if quoted:
      return "'%s'" % self.value
    else:
      return "%s" % self.value


  def add(self,var):
    try:
      self.value+=var
    except:
      self.valid=False
    return self.value    

  def sub(self,var):
    try:
      self.value-=var
    except:
      self.valid=False
    return self.value    

  def mul(self,var):
    try:
      self.value*=var
    except:
      self.valid=False
    return self.value    

  def div(self,var):
    try:
      self.value=self.value/var
    except:
      self.valid=False
    return self.value    

  def mod(self,var):
    try:
      self.value%=var
    except:
      self.valid=False
    return self.value    


  #make float() return the value
  def __float__(self):return self.value

  #make str(), repr() and comparison and numeric operators do sensible things
  def __str__(self):return str(self.value)
  def __repr__(self):return repr(self.value)
  def __cmp__(self,other): return cmp(self.value,other)
  def __nonzero__(self): return self.value and True or False
  def __coerce__(self,other): return (int(self),int(other))
  def __int__(self): return int(self.value) 
  def __long__(self): return long(self.value) 
  def __float__(self): return self.value
  def __neg__(self): return -self.value
  def __pos__(self): return +self.value
  def __abs__(self): return abs(self.value) 
#  def __invert__(self): return ~self.value
  def __add__(self, other): return self.value+other
  __radd__=__add__
  def __sub__(self, other): return self.value-other
  def __rsub__(self, other): return other-self.value
  def __mul__(self, other): return self.value*other
  __rmul__=__mul__
  def __div__(self, other): return self.value/other
  __floordiv__=__div__
  __truediv__=__div__
  def __rdiv__(self, other): return other/self.value
  __rfloordiv__=__rdiv__
  __rtruediv__=__rdiv__
  def __divmod__(self, other): return divmod(self.value,other)
  def __rdivmod__(self, other): return divmod(other,self.value)
  def __lshift__(self, other): return self.value<<other
  def __rlshift__(self, other): return other<<self.value
  def __rshift__(self, other): return self.value>>other
  def __rrshift__(self, other): return other>>self.value
  def __and__(self, other): return self.value&other
  def __rand__(self, other): return other&self.value
  def __xor__(self, other): return self.value^other
  def __rxor__(self, other): return other^self.value
  def __or__(self, other): return self.value|other
  def __ror__(self, other): return other|self.value
  def __iadd__(self, other):return self.add(other)
  def __isub__(self, other):return self.sub(other)
  def __imul__(self, other):return self.mul(other)
  def __idiv__(self, other):return self.div(other)
  __itruediv__=__idiv__
  __ifloordiv__=__idiv__

  _v_mysql_type="float"
  _v_default=0.0


def test():
  x=FLOAT('8.75')
  assert x.valid
  y=FLOAT('hello')
  assert not y.valid
  assert y==0
  y=FLOAT(7.33)
  assert y.valid
  assert x>y
  assert x.add(y)==16.08
#  print x
#  print y
#  print x*y
  x*=y
  assert int(x)==117
  assert FLOAT('2.6')/2 == FLOAT('1.3').value
  print "ok"
  

if __name__=='__main__': test()
