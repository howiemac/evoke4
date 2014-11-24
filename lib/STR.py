"""
This module implements the STR (STR) and TAG (TAG) classes, used for transient string storage and manipulation.

A TAG is an alphanumeric string 
- maximum size 64k charactersfor the entire table row... 
- typically used for  a key, or title, or single word.

For longer strings, use STR.

All values are stripped of leading and trailing whitespace.

Note that, if indexed (ie KEY), STR will be text-indexed (ie fulltext), while TAG will be field (ie standard) indexed

(Ian Howie Mackenzie - April 2007 onwards)
"""

import re

def fixed_for_sql(text):
  "makes essential fixes for use in sql"
#  return repr(self)
  return "'"+str(text).replace('\\','\\\\').replace("'","\\'")+"'"

class STR(str):
  """
  simple string handling
  """

  def __new__(self,value=""):
    if value is None:
      return str.__new__(self,"")    
    else:
      return str.__new__(self,value.strip(' '))


  def sql(self, quoted=True):
    """ gives sql string format, including quotes 
    """
    if quoted:
      return fixed_for_sql(self)
    else:
      return self

#  #the following includes bodges for handling non-ascii character - we should be using unicode both here and in database....
##  special_char_map=[("<","&lt;"),(">","&gt;"),("xc2xa3","&pound;"),("xe2x82xac","&euro;"),("xc2xa2","&cent;"),("xe2x80x93","-"),("xe2x80x9c",'"'),("xe2x80x9d",'"'),("xe2x80x99","'"),("xe2x80xa6","...")] #don't want < in output as it causes text to be skipped by the browser - also fix special symbols  
#  special_char_map=[("<","&lt;"),(">","&gt;")] # don't want < in output as it causes text to be skipped by the browser
#  replaces=dict(special_char_map)
#  replace_rule= re.compile(r'|'.join(map(re.escape,replaces.keys())))
#
#  def clean(self):
#    "replaces problem characters with browser-safe substitutes"
#    def subReplace(match):
#      return self.replaces[match.group()] 
#    return self.replace_rule.sub(subReplace,self)
 
  valid=True
  _v_default=""
  _v_mysql_type="mediumtext"

class TAG(STR):
  _v_mysql_type="varchar(255)"

  def sql(self, quoted=True):
    """ gives sql string format, including quotes. limted to first 255 chars
    """
    if quoted:
      return fixed_for_sql(self[:255])
    else:
      return self[:255]

#class URL(STR):
#  " a longer varchar for use with URLs - 2083 is maximum allowd by IE (the most restrictive browser)"
#  _v_mysql_type="char(2083)"

class CHAR(STR):
  _v_mysql_type="char(1)"

  def sql(self, quoted=True):
    """ gives sql string format, limited to first char
    """
    if quoted:
      return fixed_for_sql(self and self[0] or '')
    else:
      return self and self[0] or ''



def test():
  x=TAG('abc')
  y=TAG('hello')
  assert x<y
  assert y=="hello"
  assert x
  z=TAG()
  assert x or z
  assert x and y and not z
  assert x.sql()=="'abc'"
  z=STR(None)
  print z
  assert z==""  

if __name__=='__main__': test()
