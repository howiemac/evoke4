"""
This module implements the DATE class, used for transient date storage and manipulation.

It makes various assumptions about how dates will be used, 
and insulates the programmer from the full complexity of python date handling.

A DATE class instance wraps around a python datetime, and handles:
- input ('user') date validation and 'cleaning'
- date additions
- date comparison
- date arithmetic
- date formatting: uk date format 

relevant date fomats:
 1) user date : what the user inputs - should be same as display date but some variations allowed, eg 'dd-mm-yy' or 'dd/mm/yy'
 2) display date (or fdate) : uk display format ie 'dd/mm/yyyy'
 3) display datetime (or fdatetime) : uk display format ie 'dd/mm/yyyy hh:mm'
 4) DATE : this class wraps a python datetime object instance, used for transient storage and for manipulations 
 5) sql datetime : iso format used for sql database storage : ie 'yyyy-mm-dd hh:mm:ss'

(Ian Howie Mackenzie - November 2005)
"""

from datetime import datetime,timedelta
from time import localtime,strftime, mktime


class DATE(object):
  """
  simple date handling
  - the constructor creates self.datetime, a python datetime instance, with all its usefulness
  - the constructor shouldn't fail no matter what you throw at it, but will set self.valid accordingly
  - comparison is supported, a la datetime
  - str() and repr() return uk format date (no time) ie self.date()
  - self.time() gives uk format date and time
  - self.sql() gives sql format date
  - self.add() addition/subtraction of days, months and years to self
  """

  def __init__(self,date='now',days=0):
    """
    create the self.datetime we want, with suitable error checking
    Convert date string if possible, setting self.valid to 0 if date is not valid.
    If no date given, default of "now" gives current date and time.
    If date is None or "",  flag as invalid (and set to "1/1/1900"). 
    Add days on if given. 
    """
    self.valid=1
    if isinstance(date,datetime):#trap a datetime
      self.datetime=date
    elif isinstance(date,DATE):#trap a DATE
      self.datetime=date.datetime
      self.valid=date.valid
    elif date=='now':
      self.datetime=datetime.today()
    elif date:
      try:
        h=mn=s=0
        try: #we cant use safeint from here, so do it the hard way
          z=int(date)
        except:
          z=False   
        if z: #integer date a la mysql eg 20071003
          date=str(date) #just to make sure
          y=date[:-4]
          m=date[-4:-2]
          d=date[-2:]
        else: #user input date or date/time
          date=date.strip()
          sd=date.split()
#          print sd
          if len(sd)>1: # presumably we have time
            try:
              hms=sd[1].split(":") 
#              print 'hms',hms
              h=int(hms[0])
#              print 'h',h
              if len(hms)>=2:
                mn=int(hms[1])
#              print 'mn',mn
              if len(hms)>=3:
                s=int(hms[2])
#              print 's',s
            except:
#              raise
              pass
            date=sd[0]   
          date=date.replace('-','/').replace(' ','')# sort out minor user input anomalies
          d,m,y=date.split('/')
        #allow for shorthand years 
        y=int(y)
        y+=(y<70 and 2000 or ((y<100 and 1900) or 0))
        self.datetime=datetime(y,int(m),int(d),int(h),int(mn),int(s))
      except:#return '1/1/00' to indicate a problem
        self.datetime=datetime(1900,1,1)
	self.valid=0
	days=0 #just in case...
    else: # date is "" or None - eg mysql will return None for a blank date - default to invalid
      self.datetime=datetime(1900,1,1)
      self.valid=0
      days=0 #just in case...
    if days:
      self.datetime=self.datetime+timedelta(days=days)

  def sql(self,time=True, quoted=True):
    """ gives sql datetime format, including quotes
    """
    if quoted:
      template = "'%s'"
    else:
      template = "%s"
    if self.valid:
      if time:
        return template % str(self.datetime).split('.')[0]
      else:
        return template % str(self.datetime).split()[0]
    return template % '0000-00-00'  

  def time(self,sec=False,date=True):
    """gives uk format user date (if date is set) and time display string (to the minute only, unless sec is set) 
    """
    if self.valid:
      d=self.datetime
      if date:
        if sec:
          return  "%02d/%02d/%d %02d:%02d:%02d" % (d.day,d.month,d.year,d.hour,d.minute,d.second)
        return  "%02d/%02d/%d %02d:%02d" % (d.day,d.month,d.year,d.hour,d.minute) #works for pre 1900 dates, unlike strftime
      else:      
        if sec:
          return  "%02d:%02d:%02d" % (d.hour,d.minute,d.second)
        return  "%02d:%02d" % (d.hour,d.minute) #works for pre 1900 dates, unlike strftime
    return ''  

  def date(self):
    """gives uk format user date display string (no time) 
    """
    if self.valid:
      d=self.datetime
      return "%02d/%02d/%d" % (d.day,d.month,d.year) #works for pre 1900 dates, unlike strftime
#      return self.datetime.strftime('%d/%m/%Y')
    return ""

  def nice(self,long=True):
    """gives nice date format string eg 'on 27 Apr 07 at 12:16 - (only works for dates after 1900) - long==True gives time also' 
    """
    if self.valid:
      style=long and 'on %d %b %y at %H:%M' or '%d %b %y'
      return self.datetime.strftime(style)
    return ''  

  def add(self,years=0,months=0,days=0,hours=0,minutes=0,seconds=0):
    """ date arithmetic for years, months, days, hours, minutes, seconds
    - Adds given periods on to self.
    - This is useful because python datetimes don't deal with adding months and years.
    """
#    print "HERE"
    if years or months:
      dt=self.datetime
      d,m,y=(dt.day,dt.month+months,dt.year+years)
      while m<0:
        m+=12
        years-=1
      while m>12:
        m-=12
        years+=1    
      #adjust days using timedelta
      try:
        self.datetime=datetime(y,m,d)+timedelta(hours=dt.hour,minutes=dt.minute,seconds=dt.second)
      except ValueError:
        # Could it be the 29th February?
        if years and m==2 and d==29:
          if years>0:
            m=3
            d=1
          elif years<0:
            m=2
            d=28
          self.datetime=datetime(y,m,d)+timedelta(hours=dt.hour,minutes=dt.minute,seconds=dt.second)
        else:
          raise
    if days or hours or minutes or seconds:   
      self.datetime=self.datetime+timedelta(days=days,hours=hours,minutes=minutes,seconds=seconds)
    return self

  # representation as a counter number, which will fit a 32 bit int: seconds since 1/1/2007
  _v_erashift= -1167609600 # start at 1/1/2007

  def count(self):
    "return integer counter, being number of seconds since 1/1/2007 - self must be after 1/1/2007, or 0 is returned"
    if self.valid:
      try:
        d=self.datetime
        return int(mktime((d.year,d.month,d.day,d.hour,d.minute,d.second,0,0,-1)))+self._v_erashift
      except:
        pass	
    return 0  

  @classmethod
  def count_as_date(cls,count):
    "display integer counter a la date()"
    return strftime("%d %b %y",localtime(count-cls._v_erashift))

  # representation as a decimal - no time info

  def __int__(self):
    "return date in mysql integer date format, eg 20080822"
#    return int(self.datetime.strftime('%Y%m%d')) #doesnt work for dates before 1900
    d=self.datetime
    return d.year*10000+d.month*100+d.day

  #make str(), repr() and comparison do sensible things
  def __str__(self):return self.date()
  def __repr__(self):return ("'%s'" % self.date())

  def __cmp__(self, other): 
    try:
      return cmp(self.datetime,other.datetime)
    except:
      return False  

  def __add__(self, time):
    "add a TIME to the date or if numberish add minutes"
    # duck typing:  try to add the value
    if hasattr(time, 'value'):
      return self.add(minutes=time.value)
    # then try
    return self.add(minutes=time)

    

  _v_mysql_type="datetime"
  _v_default='0000-00-00 00:00:00'

def test():
  x=DATE('22/8/1961')
  assert x.valid
  y=DATE('22/13/1951')
  assert not y.valid
  assert x>y
  x=DATE('3/10/7')
  y=DATE('20071003')
  assert x==y
  d=DATE('')
  assert not d.valid
  # date arithmetic
  d=DATE('22/8/1961').add(years=46,months=5,days=1,hours=1,minutes=2,seconds=59)
  d.add(years=1,hours=25,minutes=61,seconds=3)
  dd=DATE('24/1/2008').add(hours=3,minutes=4,seconds=2)
  assert dd==d
  # times
  d=DATE('24/10/2013 14:18')
  assert d.time()=="24/10/2013 14:18"
  assert d.time(sec=True)=="24/10/2013 14:18:00"
  d=DATE('24/10/2013 14:18:23')
  assert d.time(sec=True)=="24/10/2013 14:18:23"
  
  #
#  print int(x)
#  print x,y
#  c=DATE().count()
#  print c
#  print DATE.count_as_date(c)
#  print DATE().sql(time=False)


if __name__=='__main__': test()



