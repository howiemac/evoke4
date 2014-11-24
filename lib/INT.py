"""
This module implements the INT class, used for transient number storage and manipulation.

An INT is an integer.

For efficiency, and maximum robustness, the .value property should be used explicitly for any numerical manipulation, though arithmetic expressions are supported.

When using built-in arithmetic expressions, floordiv is forced for /

On construction of an instance, any invalid value is forced to 0, to prevent further errors, and the valid flag is set to False. Thus INT() can be used in place of safeint()

(Ian Howie Mackenzie - January-April 2007)
"""

class INT(object):
  """
  simple integer handling
  """

  def __init__(self,var=0):
    """
    create our integer
    """
    self.valid=True
    try:
      self.value=int(var)
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
      self.value=self.value//var
    except:
      self.valid=False
    return self.value    

  def mod(self,var):
    try:
      self.value%=var
    except:
      self.valid=False
    return self.value    

  def shl(self,var):
    try:
      self.value<<=var
    except:
      self.valid=False
    return self.value    

  def shr(self,var):
    try:
      self.value>>=var
    except:
      self.valid=False
    return self.value    

  def land(self,var):
    try:
      self.value&=var
    except:
      self.valid=False
    return self.value    

  def xor(self,var):
    try:
      self.value^=var
    except:
      self.valid=False
    return self.value    

  def lor(self,var):
    try:
      self.value|=var
    except:
      self.valid=False
    return self.value    

  #make int() return the value
  def __int__(self):return self.value

  #make str(), repr() and comparison and numeric operators do sensible things
  def __str__(self):return str(self.value)
  def __repr__(self):return repr(self.value)
  def __cmp__(self,other): return cmp(self.value,other)
  def __hash__(self): 
    "value used for dictionary keys and the like"
    return self.value
  def __nonzero__(self): return self.value and True or False
  def __coerce__(self,other): return (int(self),int(other))
  def __long__(self): return long(self.value) 
  def __float__(self): return float(self.value) 
  def __neg__(self): return -self.value
  def __pos__(self): return +self.value
  def __abs__(self): return abs(self.value) 
  def __invert__(self): return ~self.value
  def __add__(self, other): return self.value+other
  __radd__=__add__
  def __sub__(self, other): return self.value-other
  def __rsub__(self, other): return other-self.value
  def __mul__(self, other): return self.value*other
  __rmul__=__mul__
  def __div__(self, other): return self.value//other
  __floordiv__=__div__
  __truediv__=__div__
  def __rdiv__(self, other): return other//self.value
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
  def __imod__(self, other):return self.mod(other)
  def __ilshift__(self, other):return self.shl(other)
  def __irshift__(self, other):return self.shr(other)
  def __iand__(self, other):return self.land(other)
  def __ixor__(self, other):return self.xor(other)
  def __ior__(self, other):return self.lor(other)

  _v_mysql_type="int(11)"
  _v_default=0

class SMALLINT(INT):
  _v_mysql_type="smallint"

class TINYINT(INT):
  _v_mysql_type="tinyint"
 

def test():
  x=INT('22')
  assert x.valid
  y=INT('hello')
  assert not y.valid
  assert y==0
  y=INT(7)
  assert y.valid
  assert x>y
  assert x.add(y)==29
  x*=y # x is no longer an INT...
  assert x==203
#  x=INT(x)
#  assert {x:y}[203]==y # FAILS O/S.....
#  assert x.value==203
  assert 196==-(y-x)
  assert y.add(8)==15
  # check for hashed equivalence
  assert INT(23)==INT(23)

if __name__=='__main__': test()
