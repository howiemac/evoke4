from domrender import Render as DomRender
from saxrender import RenderHandler
from saxdelay import OneEventDelay
from base import lib
#from base.lib import send_error
import sys
from xml.sax import parseString
import thread
from entify import decode

class SaxRender(DomRender):
  """ Drop in enhancement for domrender.Render.
      Retains dom based preprocessing, but uses
      sax to do the final rendering
  """

  DTD='<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n'
#  DTD='<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n'

  def __call__(self, ob, req):
    ""
    self.app=ob.Config.app
    self.set_key()
#    print ">>>>>>>>>KEY>>>>>>>>>>>>>>>>>>>>>>>>>>>>",self.key
    self.app_filepath=ob.Config.app_filepath+'xml/'
    self.base_filepath=ob.Config.base_filepath+'xml/' 
    env = {'ob':ob,'self':ob, self.reqname:req, 'lib':lib}
    return "%s%s" % ((not self.nowrap) and self.DTD or "",self.render(env))


  def reload(self):
    "reload the template, store the pre-processed doc as a string"
    # do our reloading in a thread safe manner
    self.acquire()
#    print  "RELOAD CALL>>>>>>>>>>>>>>>>>>>>>>>>>>>>",self.key
    try:
      if DomRender.reload(self): #this will fetch the correct template from cache (false), or construct it (true)
        self.saxdoc = self.template.toxml()
        # we don't need the DOM tree in memory until the next reload
        # let's save some memory...
        del self.template
	del self.cob.template 
	# pre-parse sax events
	self.saxevents = OneEventDelay()
        print "self.saxevents = ", self.saxevents
	# cast self.saxdoc as a string - saxparse too brittle
	# to handle unicode :(
        parseString(str(self.saxdoc), self.saxevents)  
	#put it in the cache:
        self.cob.saxevents=self.saxevents
    finally:
      self.release()

  def render(self, env):
    "render document with env environment"
    # update template if required
    if self.RELOAD:
      self.reload()
    # render using sax parser
    handler = RenderHandler(env)
    # we wrap our handler in a delay to allow read_ahead()
    # so singleton tags like <br/> are handled correctly
    #delay = OneEventDelay(handler)
    #parseString(self.saxdoc, delay)  
    #return decode(handler.out.getvalue())
    
    # pass our sax events to the RenderHandler
    self.saxevents.set_handler(handler)
    # if we have an error inside the following line, the saxevents
    # OneEventDelay needs to be reset
    try:
      results = list(self.saxevents)
    except Exception, e:
	    self.RELOAD = True
#            send_error(e, sys.exc_info())
            raise
    return decode(handler.out.getvalue())

  def __init__(self,*a, **k):
    ""
    DomRender.__init__(self, *a, **k)
    # reload lock
    self.reload_lock =thread.allocate_lock()
    self.acquire = self.reload_lock.acquire
    self.release = self.reload_lock.release
#    print 'initialising>>>>>>>>>>>>>>>>>',self.filename    
   
    
class RenderInit:
  "initialise render object & allocate locks"
  def __init__(self,*a, **k):
    ""
    SaxRender.__init__(self, *a, **k)
    # reload lock
    self.reload_lock =thread.allocate_lock()
    self.acquire = self.reload_lock.acquire
    self.release = self.reload_lock.release

class Render(SaxRender, RenderInit):
  pass


