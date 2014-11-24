""" to factor out the common pattern --

    def view(self, req, template=Render(xml/Some_method.xml)):
      req['x'] = 'waa'
      return template(self, req)

    this is replaced with a function that manipulates req, but
    does not return a meaningful value (????), and an xml template
    assumed to be found at xml/klass_method.xml

    a declaration would look like

    @template
    def view(self, req):
      req['x'] = 'waa'
    
  """
import inspect
from render import Render
from re import compile
from os.path import lexists

rx = compile('([A-Z][a-z]*)')


class Template(object):
  ""
  def __init__(self, *a, **k):
    ""
    self.a = a
    self.k = k
    
  def __call__(self, fn):
    ""
#    klass = rx.split(inspect.stack()[1][3])[1].lower()
    k=inspect.stack()[1][3]
#    print ">>>>>>>>>>>>>>>>>",k,fn.func_name
    klass = rx.split(k)[1] #we assume consistent capitalization of class / object names
#    print ">>>>klass>>>>>>>>",klass
#    print ">>>>self>>>>>>>>",self
    fname = fn.func_name

    css = []
    csspath = '../htdocs/site/%s_%s.css' % (klass, fname)
    if lexists(csspath):
      css.append('/site/%s_%s.css' % (klass, fname))
    csspath = '../htdocs/site/%s.css' % klass
    if lexists(csspath):
      css.append('/site/%s.css' % klass)

    name = '%s_%s.xml' % (klass, fname)
    template = Render(name, *self.a, **self.k)
    def function(inner_self, req):
      "a typical template"
      req['css'] = css
      req['meta'] = '%s_%d_%s' % (klass, getattr(inner_self, 'uid', 0), fname)
      fn(inner_self, req)
      return template(inner_self, req)
    return function

template = Template()
nowrap = Template(nowrap=True)
