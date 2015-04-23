""" evoke html generation:

a decorator to create simple calling functions for Evo (See evo.py)

"""

from re import compile
#from inspect import stack
from base.render.evo import Evo
import gettext
import os

class TemplateNotFound(Exception):
  "raised when no template found.  Lists the filenames tried"
  def __init__(self, templates):
    self.templates = templates
  def __str__(self):
    #return repr([i.filename for i in self.templates])
    return repr(self.templates)

class Html(object):
  "a la template.py, a decorator to create an evocative function!"

  def __init__(self, *a, **k):
    ""
    self.a = a
    self.k = k
    
#  def old__call__(self, fn):
#    ""
##    print ">>>>>>>>>>>>", fn.__name__," : ",fn.__module__
#    klass= fn.__module__.split(".")[-1]  # cheat! use the module name, as this has to be the same as the class name anyway
#    fname = fn.__name__
#    name = '%s_%s.evo' % (klass, fname)
#    template = Evo(name, *self.a, **self.k)

  def __call__(self, fn):
    "find the correct name of the template for this function then call it.  Allow for classmethods and kind override"
    fname = fn.__name__

    # we don't know much about this method at class creation time eg. it won't become a method
    # or classmethod till after this decorator is called.
    self.template_cache = {}

    def function(inner_self, req, *a, **k):
      "a typical template"

      # we know more about the method when it is called.
      # is this a classmethod?
      if type(inner_self) == type:
        klass = inner_self
      else:
        klass = type(inner_self)
      
      # Evo objects have low __init__ cost so we can keep the hierarchy in memory
      #self.templates = [Evo('%s_%s.evo' % (klassname, fname))  for klassname in [i.__name__ for i in klass.__bases__]]
      klass_names = []
      if hasattr(inner_self, '__override_classname__'):
        klass_names.append(inner_self.__override_classname__)
      klass_names += [i.__name__ for i in klass.__bases__]  

      # set req._v_template_name to allow us to access the name of the main page template from within the template or handler
      req._v_template_name=fname
      # set language
      lang = self.getLang(inner_self, req) 
      req.gettext = lang
      # run the function, and return the template
      fn(inner_self, req)
      # try each template in turn
      for klass_name in klass_names:
        template_name = '%s_%s.evo' % (klass_name, fname)
        if template_name in self.template_cache:
          template = self.template_cache[template_name]
        else:
          template = Evo(template_name)
          self.template_cache[template_name] = template
        try:
          return template(inner_self, req, gettext=lang)
        except OSError:
          pass
      # no template found in the hierarchy
      raise TemplateNotFound(['%s_%s.evo' % (klass_name, fname) for klass_name in klass_names])  
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

