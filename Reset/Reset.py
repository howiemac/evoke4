""" Password reset mechanism.  Handle forgotten passwords
    without insecure reminders.
"""
from datetime import datetime, timedelta
import uuid

from base.render import html
from base.lib import email

class Reset(object):
  "password reset mechanism"
  
  @classmethod
  def request_reset(self, req):
    "a reset has been requested.  Expects req.username or req.email"
    if not(req.username or req.email):
      req.error = "Please provide an email or user name."
      return self.User.get(1).reminder_form(req)
    user = None
    l = self.User.list(id=req.get('user', '')) 
    if l:
      user = l[0]
    else:
      l = self.User.list(email=req.get('email', ''))
      if l:
        user = l[0]

    # no user? No reminder.
    if not user:
      req.error = 'No user was found using the supplied username or email.'
      return self.User.get(1).reminder_form(req)

    # we have a user.  Create a Reset record and send an aposite email
    r = self.new()
    r.user = user.uid
    r.ts = datetime.now()+timedelta(minutes=15)  
    r.key = uuid.uuid4().hex
    r.stage = 'requested'
    r.flush()

    html = """
      <p>We have received a request to reset the password on %s associated with this email account.   If you have not made such a request please disregard this email.</p>

      <p>If you do want to reset this password please click on <a href="%s">this link</a> and follow the instructions provided.</p>
""" % (self.Config.domains[0], r.url('reset_password', key=r.key))
    email(self.Config.mailfrom, )
      
