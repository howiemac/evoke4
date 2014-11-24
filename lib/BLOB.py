"""
This module implements the BLOB class.

(Ian Howie Mackenzie - July 2007)
"""

import MySQLdb

class BLOB(str):
  """
  simple blob handling
  """

  def __new__(self,data=""):
    self.data=data

  def sql(self, quoted=True):
    """ gives sql string format, including quotes 
    """
    if quoted:
      return '"%s"' % MySQLdb.escape_string(str(self.data))
    else:
      return '%s' % MySQLdb.escape_string(str(self.data))

  def __str__(self):
    if type(self.data)==type(''):
      return self.data
    else:#must be array
      return self.data.tostring()

  def __repr__(self):
    return repr(self.data)


  valid=True
  _v_default=""
  _v_mysql_type="blob"

def test():
  pass

if __name__=='__main__': test()
