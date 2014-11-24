""" evoke html generation:

a decorator to create simple calling functions for Evo (See evo.py)

"""

from re import compile
#from inspect import stack
from base.render.evo import Evo
import gettext
import os

class Html(object):
  "a la template.py, a decorator to create an evocative function!"

  def __init__(self, *a, **k):
    ""
    self.a = a
    self.k = k
    
  def __call__(self, fn):
    ""
#    print ">>>>>>>>>>>>", fn.__name__," : ",fn.__module__
    klass= fn.__module__.split(".")[-1]  # cheat! use the module name, as this has to be the same as the class name anyway
    fname = fn.__name__
    name = '%s_%s.evo' % (klass, fname)
    template = Evo(name, *self.a, **self.k)

    def function(inner_self, req, *a, **k):
      "a typical template"
      # set req._v_template_name to allow us to access the name of the main page template from within the template or handler
      req._v_template_name=fname
      # set language
      lang = self.getLang(inner_self, req) 
      req.gettext = lang
      # run the function, and return the template
      fn(inner_self, req)
      return template(inner_self, req, gettext=lang)
    return function

  def getLang(self, inner_self, req):
    "return gettext language object"
    code = req.cookies.get('lang', '')
#    print "getLang", code
    if code:
      try:
        trans_domain = inner_self.Config.appname
        trans_path = os.path.join(inner_self.Config.app_fullpath, 'trans')
        lang = gettext.translation(trans_domain, trans_path,  languages=[code])
#        print "lang found", lang, type(lang)
      except:
      # fallback on plain, no-op gettext
#        print "lang not found"
        lang = gettext
      return lang.gettext
    else:
#      print "no language specified"
      return gettext.gettext


html = Html()

