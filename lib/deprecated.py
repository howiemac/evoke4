"""
deprecated library routines  (retained for backwards compatibility only - do not use otherwise)
===============================================================================================

class deepdate		     use DATE


def hours(text,negate=0):    converts input string, or number of minutes, to display format ie 'hh:mm'
			     returns '' rather than '0:00'
			     allows for text fractions eg '1.5' giving '1:30'
			     note: value() converts the opposite way
def value(text):             converts 'money' format string to long integer in pence, 
			     converts 'hours' format string to minutes long integer
			     returns 0 for empty or invalid strings
			     if it gets a number, returns that as long integer
def money(text,negate=0,zeros=0):  converts input string, or number of pence, to user 'money' text format ie '?.??'

def redirect(req,url): does a response redirect, ie http status code 302 - use as: return redirect(req,url)

greenstripe="#C8F8E8"
greystripe="#AAAAAA"
red="red"
yellow="yellow"
orange="#FF6600"
green="green"
cyan="#0066CC" #"cyan"
blue="blue"
black="black"

(IHM April 2007)


"""

from DATE import DATE as deepdate
import re

###################### time ###################

def _hours(text,rex=re.compile('(-?)([0-9]*)\:?([0-5]?[0-9]?)')):
  """ used by hours() and value()
  """
  return rex.match(text).groups()
  
def hours(text,negate=0):
  """ converts input string, or number of minutes, to display format ie 'hh:mm'
      returns '' rather than '0:00'
      allows for text fractions eg '1.5' giving '1:30'
      note: value() converts the opposite way
  """
  try:# catch decimal fractions entered as text
    text=float(text)
  except:
    pass  
  if type(text)!=type(''): #if not a string, assume we have a number
    try:
      text="%d:%s" % divmod(int(text*60),60) 
    except:
      return ''
  sign,hours,minutes = _hours(text)
  if negate: #toggle sign
    sign=sign and ' ' or '-'
  text="%s%s:%s" % (sign,hours or '0',minutes.zfill(2))
  return text!="0:00" and text or ""

####################### money ##############

def value(text):
  """converts 'money' format string to long integer in pence, 
     converts 'hours' format string to minutes long integer
     returns 0 for empty or invalid strings
     if it gets a number, returns that as long integer
  """
  if type(text)!=type(''): #if not a string, perhaps it is already a number? 
    return safelong(text)
  try:
    sign,pounds,pence=_money(text.strip())
    v= (safelong(pounds)*100L)+safelong(pence)
    return sign and -v or v
  except:
    try: #have we 'hours' format?
      sign,hours,minutes=_hours(text)
      return (safelong(hours)*60L)+safelong(minutes)
    except:
      return 0L

def _money(text,rex=re.compile('(-?)([0-9]*)\.?([0-9]*)')):
  """ used by money() and value()
  """
  return rex.match(text).groups()

def money(text,negate=0,zeros=0):
  """ converts input string, or number of pence, to user 'money' text format ie '?.??'
  """
  if type(text)!=type(''): #if not a string, assume we have a number
    try:
      text=str(text) #convert to string
      if (len(text)==1):
        text='0'+text
      elif ((len(text)==2) and (text[0]=='-')): 
        text='-0'+text[1]
      text="%s.%s" % (text[:-2] ,text[-2:])# add decimal point
    except:
      return ''
  text=text.replace(',','') #remove all commas 
  sign,pounds,pence=_money(text)
  if pounds=='' and pence=='00':
    return ''
  if negate: 
    sign=(not sign) and '-' or ''
  pence=pence and (pence+'0')[:2] or '00'
  return "%s%s.%s" % (sign,pounds or '0',pence)



################### html formattingr ###################

# colour constants:
greenstripe="#C8F8E8"
greystripe="#AAAAAA"
red="red"
yellow="yellow"
orange="#FF6600"
green="green"
cyan="#0066CC" #"cyan"
blue="blue"
black="black"


