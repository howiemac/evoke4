"""
evoke library routines

a library of robust general routines mainly for handling conversions

def elapsed(seconds)         converts time in seconds into hours:mins:secs   

def process_time():          returns time elapsed since system started, in a display format

def httpDate(self, when=None, rfc='1123'): generates rfc standard dates strings for http 

def turnaround(start,end):   calculates turnaround, in working days, ie ignoring weekends
                             accepts dates in any format  

def asItems(text):
def counted(items,start=1):  converts list of items into list of (count,item) pairs
def safelong(num):           converts to longint, regardless
def safeint(num):            converts to int, regardless
def sn(ok):                  converts boolean value to +1 or -1

def limit(v,lo,hi):          limits v to between lo and hi

def percent(a,b):            returns string repr of a as a percentage of b (to nearest full percent)

def email(FROM,TO,text,html=0):	sends an email message - defaults to plain text

def page(req,pagesize=50):   returns limit parameter for self.list()

def idf(t):                  fixes t into an id which wont break html - not foolproof

def url_safe(text):          fixes url for http

def csv_format(s):           cleans syntax problems for csv output

def sql_list(val):	     converts single value or list or tuple into sql format list for 'is in' etc.

(Ian Howie Mackenzie 2/11/2005 onwards. Email enhancements by Chris J Hurst)
"""

from time import time,gmtime
import datetime 
from DATE import DATE 
import urllib,re

###################### time ###################

def httpDate(when=None, rfc='1123'): 
    """ (copied as is from MoinMoin request.py)
    Returns http date string, according to rfc2068

    See http://www.cse.ohio-state.edu/cgi-bin/rfc/rfc2068.html#sec-3.3

    A http 1.1 server should use only rfc1123 date, but cookie's
    "expires" field should use the older obsolete rfc850 date.

    Note: we can not use strftime() because that honors the locale
    and rfc2822 requires english day and month names.

    We can not use email.Utils.formatdate because it formats the
    zone as '-0000' instead of 'GMT', and creates only rfc1123
    dates. This is a modified version of email.Utils.formatdate
    from Python 2.4.

    @param when: seconds from epoch, as returned by time.time()
    @param rfc: conform to rfc ('1123' or '850')
    @rtype: string
    @return: http date conforming to rfc1123 or rfc850
    """
    if when is None:
      when = time()
    now = gmtime(when)
    month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][now.tm_mon - 1]
    if rfc == '1123':
      day = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][now.tm_wday]
      date = '%02d %s %04d' % (now.tm_mday, month, now.tm_year)
    elif rfc == '850':
      day = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][now.tm_wday]
      date = '%02d-%s-%s' % (now.tm_mday, month, str(now.tm_year)[-2:])
    else:
      raise ValueError("Invalid rfc value: %s" % rfc)
    return '%s, %s %02d:%02d:%02d GMT' % (day, date, now.tm_hour, now.tm_min, now.tm_sec)

def elapsed(seconds,format=""):
    """converts time in seconds into days hours mins secs 
    format, if given, can be "d:h:m:s", or "h:m:s", or "m:s", otherwise long format is used
    ( adapted from zope ApplicationManager.py )
    """ 
    s=safeint(seconds) 
    d=0
    h=0
    if (not format) or format.startswith("d:"):
      d=int(s/86400)
      s=s-(d*86400)
    if (not format) or ("h:" in format):
      h=int(s/3600)
      s=s-(h*3600)
    m=int(s/60)
    s=s-(m*60) 
    if format:          
      if d:
        return ('%d:%02d:%02d:%02d' % (d, h, m, s))
      if h:
        return ('%d:%02d:%02d' % (h, m, s))
      return ('%d:%02d' % (m, s))
    else: # long format     
      d=d and ('%d day%s'  % (d, (d != 1 and 's' or ''))) or ''
      h=h and ('%d hour%s' % (h, (h != 1 and 's' or ''))) or ''
      m=m and ('%d min' % m) or ''
      s='%d sec' % s
      return ('%s %s %s %s' % (d, h, m, s)).strip()

def process_time():
    s=int(time())-process_start
    return elapsed(s)

process_start=int(time())

def turnaround(start,end):
    """calculates turnaround, in working days, ie ignoring weekends
       accepts dates in any format  
    """
    start=DATE(start).datetime.date()
    end=DATE(end).datetime.date()
    t = end-start
    s = start.weekday()
    e = end.weekday()
    d = (7-s) + e
    return int ((((t.days-d)*5)//7)+d-1)


###################### number conversion ###################

def asItems(text):
    try:
	n = int(text)
	if n==0: 
	    return ''
	return `n`
    except:
	return ''

def counted(items,start=1):
   "converts list of items into list of (count,item) pairs"
   n=start
   z=[]
   for i in items:
     z.append((n,i))
     n+=1
   return z

def safelong(num):
  """converts to longint, regardless
  """
  try:v=long(num)
  except:v=0L 
  return v  

def safeint(num):
  """converts to int, regardless
  """
  try:v=int(num)
  except:v=0
  return v  

def safefloat(num):
  """converts to float, regardless
  """
  try:v=float(num)
  except:v=0.0
  return v  

def sn(ok):
  """converts boolean value to +1 or -1
  """
  if ok:return 1
  else: return -1      

# number utilities ##################

def limit(v,lo,hi):
  "limits v to between lo and hi"
  return min(hi,max(lo,v))

# number formatting ############
  
def percent(a,b):
  "returns string repr of a as a percentage of b (to nearest full percent)"
  return '%d%%' % (0.5+float(a)*100/float(b))

################# list utilities ###############

def prev(p,seq):
  "expects current object 'p', and sequence of objects 'seq' - returns previous object"
  try:
    i=seq.index(p)
    if i:
      return seq[i-1]
    else:
      return None  
  except:
    return None
  
def next(p,seq):
  "expects current object 'p', and sequence of objects 'seq' - returns next object"
  try:
    return seq[seq.index(p)+1]
  except:
    return None

################## email #######################

from email.MIMEMultipart import MIMEMultipart 
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import Encoders
import smtplib

def email(FROM,TO,subject="", text="",html="",SMTP='127.0.0.1',LOGIN=[], sender="", replyto="", attachments={}):
  """send a multipart plain text (or html) message, using given SMTP
  - Optional LOGIN (ie SMTP validation) must give (<user>,<password>)
  - allows for a list of recipients in TO: each gets a separate email, ie bcc

  - attachment expects a dictionary of {filename:content}
  """
  if not (FROM and TO and SMTP):
 #   print "EMAIL DISABLED >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    return # email is disabled or invalid, so do nothing
  # set up our message
  root = MIMEMultipart('related')
  root['Subject'] = subject
  if sender:
    root['From'] = '"%s" <%s>' % (sender, FROM)
  else:
    root['From'] = FROM
  if replyto:
    root['Reply-To'] = replyto
  if isinstance(TO,basestring):
    TO=[TO]
  root.preamble = 'This is a multi-part message in MIME format.'
  # add our alternative versions
  alt = MIMEMultipart('alternative')
  root.attach(alt)
  if html:
    alt.attach(MIMEText(html, 'html'))
  else:  
    alt.attach(MIMEText(text))

  # include attachments
  for filename,content in attachments.items():
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(content)
    Encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename=%s' % filename)
    root.attach(part)

  # send our message(s)
  try:
    smtp = smtplib.SMTP()
    smtp.connect(SMTP)
    if LOGIN:
      smtp.login(*LOGIN)
    for t in TO: 
      try:
        root['To']=t
        smtp.sendmail(FROM, t, root.as_string())
#        print "SENT: FROM=",FROM,' TO=',t,' ROOT=', root.as_string()
	del root['To'] # need to del this, as the message class __setitem__ appends rather than replaces
      except: 
        print "SENDMAIL REFUSAL: FROM=",FROM,' TO=',t,' ROOT=', root.as_string()
    smtp.quit()
  except:
    print "SMTP CONNECT ERROR: FROM=",FROM,' TO=',TO,' ROOT=', root.as_string()




################### paging ####################

def page(req,pagesize=50):
    "returns limit parameter for self.list(): requires req.pagenext, and provides req.pagenext and req.pagesize"
    offset=safeint(req.pagenext)                                                                                          
    req.pagenext=offset+pagesize #next page
    req.pagesize=pagesize #for use in form, to determine whether there is more to show
    return '%s,%s' % (offset,pagesize)

################### html formattingr ###################

def idf(t):
    "fixes t into an id which wont break html - not foolproof"
    return t.replace(' ','').replace('(','').replace(')','')

################### http formattingr ###################

#def url_safe(text):
#  return urllib.quote(text)    

def url_safe(text):
  return urllib.quote_plus(text,safe="/")    


################### CSV formattingr ###################
# O/S - THIS SHOULD BE SOMEWHERE ELSE.... a reporting library?

def csv_format(s):
  """
    cleans syntax problems for csv output
  """
  s=s.replace('"',"'")
  s=s.replace("\n", " ")
  s=s.replace("\x00D","")
  return '"%s"' % s

################# SQL formatting ###################

def sql_list(val):
  "converts list or tuple into sql format list for 'is in' etc." 
  return len(val)==1 and '(%s)' % `val[0]` or tuple(val)

################ filename formatting ###############

def safe_filename(text):
  "not foolproof"
  return text.replace(' ','_').replace("'","").replace('"','').replace('/','-').replace('?','').replace('!','')
  
  
def test():
  pass


if __name__=='__main__': test()

  
