"""
This module implements the FLAG class, used for transient date storage and manipulation.

A FLAG is a boolean flag, with value "" or "Y"

(Ian Howie Mackenzie - April 2007)
"""

class FLAG(object):
  """
  simple boolean handling
  """

  def __init__(self,var=""):
    """
    create our string
    """
    self.valid=True 
    try:
      self.value=var and "Y" or ""
    except:
      self.value=""
      self.valid=False
      
  def sql(self, quoted=True):
    """ gives sql string format, including quotes
    """
    if quoted:
      return "'%s'" % self.value
    else:
      return self.value

  #make str(), repr() and comparison do sensible things
  def __str__(self):return self.value
  def __repr__(self):return repr(self.value)
  def __cmp__(self,other): return cmp(bool(self.value),other)
  def __nonzero__(self): return self.value and True or False

  _v_mysql_type="char(1)"
  _v_default=""

def test():
  x=FLAG(1)
  assert x.valid
  y=FLAG(0)
  assert y.valid
  z=FLAG(1)
  assert x
  assert x or y
  assert x or False
  assert not y
  assert x and not y
  assert x==z
  assert not (x!=z)
  assert x==True
  assert True==x
    

if __name__=='__main__': test()
