"""
This module implements the MONEY class,
used for transient storage and manipulation of financial amounts.

A MONEY stores money in pence as a longinteger.

(Ian Howie Mackenzie - April 2007)
"""
from decimal import Decimal
import re
from INT import INT


class MONEY(INT):
  """
  simple money handling
  """

  def __init__(self, var=0):
    """
    create our longinteger
     converts 'money' format string to longinteger in pence,
     returns 0 for empty or invalid strings
     if it gets a number, returns that as a longinteger
    O/S need to cope with currencies and other currency formats
    """
    self.valid = True
    self.value = 0
    MONEY = self.__class__
    if isinstance(var, MONEY):  # trap a MONEY
      self.value = var.value
      self.valid = var.valid
    else:
      try:
        # if type(var) == type(''):
        if isinstance(var, str):
          self.value = self._f_str_to_money(var)
        else:  # if not a string, perhaps it is already a number?
          self.value = long(var)
      except:
        self.valid = False

  def _f_str_to_money(self, text, rex=re.compile('(-?)([0-9]*)\.?([0-9]*)')):
    ""
    text = text.strip().replace(',', '')  # remove all commas
    return int(Decimal(text)*100)
    # sign,pounds,pence=rex.match(text).groups()
    # v= (long(pounds)*100L)+long(pence)
    # return sign and -v or v

  def _f_money_to_str(self, amount, profile=re.compile(r"(\d)(\d\d\d[.,])")):
    """converts money longint to a string representation, with thousand
       separators, and decimal point"""
    temp = "%.2f" % (float(amount)/100,)
    while 1:
      temp, count = re.subn(profile, r"\1,\2", temp)
      if not count:
        break
    return temp

# alternative:
#    locale.setlocale(locale.LC_ALL,('en','latin'))
#    return locale.format_string('%.2f',float(value)/100, True)

  def negate_if(self, negate=True):
    """ flip the sign for display purposes
    """
    return self._f_money_to_str(negate and -self.value or self.value)

# ##make str(), repr() do sensible things ###########

  def __str__(self):
    "output as ?,???.??"
    return self._f_money_to_str(self.value)

  __repr__ = __str__

  def __cmp__(self, other):
    try:
      return cmp(long(self), long(other))
    except:
      return False

  def __coerce__(self, other):
    return (long(self), long(other))

  def __int__(self):
    return int(self.value)

  def __long__(self):
    return self.value

  _v_mysql_type = "bigint(20)"


def test():
  x = MONEY('1,234.99')
  assert x.valid
  assert x.value == 123499
  assert str(x) == '1,234.99'


if __name__ == '__main__':
  test()
