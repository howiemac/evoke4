""" format an exception so 
    it can be sent as an email
"""
import sys
from library import email


class Formatter(object):
  def __init__(self, e, exc_info):
    ""
    self.e = e
    self.exc_info = exc_info
    traceback = exc_info[2]
    trace = []
    while traceback is not None:
      frame = traceback.tb_frame
      lineno = traceback.tb_lineno
      code = frame.f_code
      filename = code.co_filename
      name = code.co_name
      trace.append((filename, lineno, name))
      traceback = traceback.tb_next
    self.trace = trace
 
  def format(self): 
    s = '\n'.join('**File: %s, line %s, in %s' % line for line in self.trace)
    s += "\n%s: %s" % (self.e.__class__.__name__, str(self.e))
    return s

  def format(self):
    wrap = """
    <table style="text-align:left;border:1px solid black">
      <tr>
        <th>file</th>
        <th>line</th>
        <th>name</th>
      </tr>
      %s
      <tr>
        <td>
          %s
        </td>
        <td colspan="2">
          %s
        </td>
      </tr>
    </table>
    """
    l = '\n'.join('<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % line for line in self.trace)
    return wrap % (l, self.e.__class__.__name__, self.e)

def error(e, exc_info):
  "format error"
  return Formatter(e, exc_info).format()

def send_error(self, e, exc_info, efrom='', eto=''):
  subject = e.__class__.__name__  
  html = Formatter(e, exc_info).format()
  email(efrom or self.Config.mailfrom or self.Config.bugmailto, eto or self.Config.bugmailto, subject, html=html,SMTP=self.Config.SMTPhost,LOGIN=self.Config.SMTPlogin)

def test():
  try:
    # spot the deliberate mistake
    MySQLdb.connect('', 'wawa', 'aaa')
  except Exception, e:
    send_error(e, sys.exc_info(),'chris@chrishurst.co.uk','chris@chrishurst.co.uk')
    #print Formatter(e, sys.exc_info()).format()

if __name__=='__main__':
  test()
