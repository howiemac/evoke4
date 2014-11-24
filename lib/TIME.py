"""
This module implements the TIME class, used for transient storage and manipulation of time slices.

A TIME stores time in minutes as a longinteger.

(Ian Howie Mackenzie - April 2007)
"""

import re
from MONEY import MONEY

class TIME(MONEY):
  """
  simple TIME handling
  """

  def __init__(self,var=0):
    """
    create our longinteger
     converts 'TIME' format string to longinteger in minutes, 
     returns 0 for empty or invalid strings
     if it gets a number, returns that as a longinteger
    """
    self.valid=True
    self.value=0
    if isinstance(var,TIME):#trap a TIME
      self.value=var.value
      self.valid=var.valid
    else:
      try:
        if type(var)==type(''): 
          self.value=self._f_str_to_hours(var)
        else:#if not a string, perhaps it is already a number? 
          self.value=long(var)
      except:
#        raise
        self.valid=False	

  def _f_str_to_hours(self,text,rex=re.compile('(-?)([0-9]*)\:?([0-5]?[0-9]?)')):
    """ converts display format to number of minutes (longint)
    """
    sign,hours,minutes=rex.match(text).groups()
    v=(long(hours)*60L)+long(minutes)
    return sign and -v or v

  def _f_hours_to_str(self,amount):
    """ converts number of minutes to display format ie 'hh:mm'
    """
    return "%01d:%02d" % divmod(amount,60) 

  def negate_if(self,negate=True):
    """ flip the sign for display purposes
    """
    return self._f_hours_to_str(negate and -self.value or self.value)

###make str(), repr() do sensible things ###########

  def __str__(self):
    return self._f_hours_to_str(self.value)

  __repr__=__str__



def test():
  x=TIME('12:59')
  assert x.valid
  assert str(x)=='12:59'


if __name__=='__main__': test()
