"""
evoke base request object
"""
import sys
import time
from copy import copy
from urllib import quote

try:
  import user_agents
except ImportError:
  print """user_agents module not found.
    See https://pypi.python.org/pypi/user-agents/"""
  user_agents = None

# Session based cache
from zope.interface import Interface, implements  # , Attribute
from twisted.python.components import registerAdapter
from twisted.web.server import Session

from base.lib import DATE, httpDate



class ISessionCache(Interface):
  "Session Cache interface"


class SessionCache(object):
  "arbitary session storage"
  implements(ISessionCache)

  def __init__(self, session):
    ""

# register session cache
# plumbing
registerAdapter(SessionCache, Session, ISessionCache)
#print "registerAdapter"


class Reqbase(dict):
  """ extend the dict object with our own extra methods
  """

  def redirect(self, url,permanent=False,anchor=""): 
    """Cause a redirection without raising an error 
    - accepts full URL (eg http://whatever...) or URI (eg /versere/Account/2/view)
    - retains anchor and messages
    """
    url=str(url).strip()#safety first - defend against unicode, which will break both http and string matching
#    print "REDIRECT:",url
    if not url.startswith('http'): 
      url="http://%s%s" % (self.get_host(),url)
#    print "REDIRECT full url:",url or "no url", " == anchor: ", anchor or "no anchor"
    if '#' in url:
      url,anchor=url.rsplit('#',1)
    ats= self.error and ['error=%s' % quote(self.error)] or []
    if self.warning:
      ats.append('warning=%s' % quote(self.warning))
    if self.message:
      ats.append('message=%s' % quote(self.message))
    q= url.find('?')>-1 and "&" or "?"
    ats=ats and (q+'&'.join(ats)) or "" 
#    print "REDIRECT with ats: ",url or "no url", "ats=",ats, "anchor=",anchor or "no anchor"
    url='%s%s%s%s' % (url,ats,anchor and '#' or '',anchor)
#    print "REDIRECT FINAL URL:", url  
#    print " "
    # do the redirect
    self.request.setResponseCode(permanent and 301 or 302,None)
    self.request.setHeader('Location', url)
    return " " #return a True blank string, to indicate we have a page result


  def set_cookie(self, id, data="", expires=None, domain=None,
                 path="/", max_age=None, comment=None, secure=None):
    """set defaults, translate expires from seconds to http date,
       and call the twisted method"""
    when = expires and (httpDate(time.time()+expires, rfc='850')) or None
#    print "when=", when
    self.request.addCookie(id, data, when, domain, path, expires or max_age,
                           comment, secure)

  def clear_cookie(self, id):
    "cookie is cleared by setting it to expire a year ago!"
#    print "CLEARING COOKIE"
    self.set_cookie(id, expires=-3600*24*365, max_age=0)

  def get_host(self):
    "host domain"
    host = self.request.requestHeaders.getRawHeaders('host')[0]
    try:
      host= self.request.requestHeaders.getRawHeaders('x-forwarded-host')[0]
    except:
      pass
    return str(host)

  def get_path(self):
    "path"
    return str(self.request.path)

  def get_uri(self):
    "uri"
    return str(self.request.uri)

  def __copy__(self):
    "make this copyable by copy.py"
    return self.__class__(copy(dict(self)))


class Req(Reqbase):
  """dict / object hybrid - CJH- stores form fields as a dictionary,
  but allows them to be set and got as req properties.
  WEAKNESS: if a form field uses a string method name as a key,
  then that field can only be set and got using req.[key] syntax
  ADVANTAGE:  allows backward compatibility, and the direct use of
  dictionary methods and operands
  """

  def __getattribute__(self, k):
    if hasattr(Reqbase, k):
      return dict.__getattribute__(self, k)
    else:  # do an implicit get
      # TODO - should this raise an error for an unknown key?
      return self.get(k, "")

  def __setattr__(self, k, v):
    if hasattr(Reqbase, k):
      dict.__setattr__(self, k, v)
    else:
      self[k] = v


def respond(request, dispatcher):
  "initialise req from the Twisted request, then call the dispatcher"
  # First we need to transform the request into our own format
  # our format is {key:value, .., cookies:{key:value}, request:request}
  req = Req()
  # retain multiple value args as a list
  req.update(dict([(i[0], len(i[1]) > 1 and i[1] or i[1][0])
                   for i in request.__dict__['args'].items()]))
  req.cookies = request.__dict__['received_cookies'] or {}

  # if we have the relevant modules then add user agent information
  if user_agents:
    ua_string = request.getHeader('user-agent')
    req.user_agent = user_agents.parse(ua_string or '')
  else:
    req.user_agent = None
  req.request = request

  # set up Session cache
  session = request.getSession()
  req.cache = ISessionCache(session)

  # get the domain and port
  req._v_domain = req.get_host().split(":")[0]  # excludes port
  # Now process the request
  path = request.__dict__['path']
  try:
    result = dispatcher.request(path, req)
  except:
    raise
    sys.stderr.write(DATE().time())
    sys.stderr.write(path+'\n')
    result="request error..."
  return result


def test():
  ""
  r = Req()
  # non-dict key
  r.pie = 400
  assert r.pie == r['pie'] == 400, "non dict keys noworks"
  # dict key
  r.copy = 401
  assert 'copy' not in r, "dict keys should not be items"
  assert r.copy == 401, "dict keys should be set as attributes"
  assert r.wrong == "", "invalid attribute should return an empty string "
if __name__ == '__main__':
  test()
