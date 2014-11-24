"""
Simple Rendering System

CJH

enhanced by IHM April 2007 to allow for base/xml and app/code/xml overrides

WOULD BE NICE (per IHM): 
 - make wrapper reload when it has changed, regardless of whether parent has changed (and thus make parent reload also)
 - don't reload wrapper when it doesn't need to...)
 - ditto for include templates
 - better syntax for include parameter passing....

TODO (per CJH): Make repeat variable available to atts in same tag so you can <option repeat='..' atts='..'  />
"""
from xml.dom.minidom import parseString
from xml.dom import NotFoundErr
from base import lib
from domiter import get_elements_by_id
import itertools
from base.lib import Error #, send_error
import gc
import time
import os
import sys
from os.path import lexists
from entify import encode

def parse(doc):
  "parse to dom, hiding entities"
  try:
    s = open(doc).read()
    return parseString(encode(s))
  except Exception, e:
#    send_error(e, sys.exc_info())
    raise

class ExpressionError(Error):
  "Expression Error: %s"

class CacheObject(object):
  "all cache code is in reload()"
  def __init__(self):
    self.path=""
    self.saxevents="" #we may need this dummy...

class Render:
  RELOAD = True	# check for template changes before rendering 
  DOM_CLASSES = 'Document Element'.split()
  wrapper="wrapper.xml"
  cache={} #this is required for multi to work, with local template overrides (Ian 5/4/7)

  def __init__(self, filename, namespace='', reqname='req', nowrap=False, wrapper=None):
    "namespace and req allows us to do several rendering phases like <namespace>:atts='x=<reqname>['waa']'"
    self.filename = filename
    self.path="" #this will be set later... 
#    print ">>>>>>>>>>>>>>>>>>>>>>>>>>>DOMRENDER INIT"
    self.namespace = namespace and namespace+'.' or ''
    self.reqname = reqname
    self.nowrap = nowrap
    if wrapper:
      self.wrapper = wrapper
    self.timestamp = None
    #self.reload()
    self.expanded = 0
    self.errors = []
    self.permit = ''
 
  def __call__(self, ob, req):
    # check for permissions here. return not permitted if required
    # get the user's identity
    # if not allowed, return 'not allowed page'    
    # check if user has the permit for this template
    if (not self.permit) or req.user.can(self.permit.split('.',1)):    
      data = {'ob':ob,'self':ob, self.reqname:req, 'lib':lib}
      return self.render(data)
    else:
      return self.noway(req)

  def noway(self, req):
    "permission denied"
    return 'No way.'

  def set_key(self):
    "sets the cache key"
    self.key="%s.%s" % (self.app,self.filename.replace('.xml',''))

  def reload(self,force=False):
    "reload the template, if it is not in the cache, or the timestamp doesn't match"
    cob=self.cache.get(self.key,CacheObject())
    if (cob.path and not force):#is it in the cache?
      if (cob.timestamp == os.stat(cob.path).st_mtime):# does the timestamp match?
#        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> MATCHED",self.key
        self.path=cob.path
        self.wrapperpath=cob.wrapperpath
        if hasattr(cob,'template'):
          self.template=cob.template
	self.saxevents=cob.saxevents
        return False # the correct template objects are now copied from cache
    else:  #ie do this first time only.. get the paths  (we could not do this before now, because we didn't have the base and app filepaths)
      cob.path=self.app_filepath+self.filename#is there local template?
      if not lexists(cob.path):
        cob.path=self.base_filepath+self.filename# use the base template
      cob.wrapperpath=self.app_filepath+self.wrapper# is there a local wrapper?
      if not lexists(cob.wrapperpath):
        cob.wrapperpath=self.base_filepath+self.wrapper# use the base wrapper
#    print "WRAPPERPATH=",self.wrapperpath,self.app_filepath,self.wrapper
#    print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>RELOAD>>",self.key
    self.path=cob.path
    self.wrapperpath=cob.wrapperpath
    self.template=cob.template= self.wrapTemplate(self.path, self.wrapperpath)
    self.include(self.template.childNodes[0])
    self.timestamp=cob.timestamp=os.stat(cob.path).st_mtime            
    self.cache[self.key]=cob #cache the template
    self.cob=cob #we need this in render.py for sax data
    # return true to indicate reload has happened
    return True

  def render(self, alldata):
    "render document with alldata"
    self.alldata = alldata
    # reload if templates are under development
    if self.RELOAD:
      self.reload()
    self.doc = self.template.cloneNode(deep=1)
#    self.include(self.doc.childNodes[0])
    self.expand(self.doc.childNodes[0], alldata)
    self.noteErrors()
    result = self.doc.toxml()
    del self.alldata
    del self.doc
    gc.collect()
#    result = 'notaresult'
    return result

  def include(self, here):
    """replace tag contents with content of external doc's <body> tag
       do it recursively before we attempt any other substitution"""
    if here.nodeType == here.ELEMENT_NODE:
      include = here.getAttribute(self.namespace+'include')	
      #### alter include syntax to include parameters.. include='xml/blah.xml;x=100,y=[],z=someexpr' -> template(params={...})
      if include:
        # parse the include attribute
        if ';' in include:
          path, data = include.split(';',1)
          data = eval('dict(%s)' % data)
        else:
          path, data = include, {}
        #### apply rendering to frag here. Use a different set of tag names????
        #### we need a Render instance to do pre-rendering at include time.  How convoluted. May move namespace and reqname
        #### parameters to expand method?
        template  = Render(path, namespace='include', reqname='param', nowrap=True) # this will render include.blah tags using param instead of req
        template.app=self.app#set_key needs this
        template.set_key()
        template.app_filepath=self.app_filepath#reload needs this
	template.base_filepath=self.base_filepath#reload needs this
        template.reload(force=True)
        template.doc = template.template  # we only expand this once, so no need to retain original template's structure
        template.expand(template.doc.childNodes[0], data={template.reqname:data})
        frag = template.template.getElementsByTagName('body')[0]
        frag.tagName='div'
        self.replace(here, frag)
	# we've been replaced, so we need to recurse through the frag
	here = frag
      for node in here.childNodes:
        self.include(node)

  def wrapTemplate(self, doc, wrap):
    """Wrap the document in a standard wrapper.
       Move the contents of the document's <body> tag
       into the wrapper element with id=content

       doc, wrapper are paths
    """
    doc = parse(doc)
    wrap = parse(wrap)
    # if there's a nowrap attribute, then we send back the template unwrapped
    # we can specialise this if it turns out to be useful
    if not doc.getElementsByTagName('html'):
      return doc
    html = doc.getElementsByTagName('html')[0]
    # extract permit information for this template
    if html.hasAttribute('permit'):
      self.permit = html.getAttribute('permit')
      html.removeAttribute('permit')
    else:
      self.permit = ''
    if html.hasAttribute('nowrap'):
      html.removeAttribute('nowrap')
      return doc
    if self.nowrap:
      return doc
    # we will be replacing the element with id='content' with a div of content
    insert_point = get_elements_by_id(wrap.getElementsByTagName('html')[0], 'content').next()
    content = doc.getElementsByTagName('body')[0].cloneNode(deep=True) 
    content.tagName = 'div'
    self.replace(insert_point, content)
    return wrap

  def expand(self, here, data):
    "recursively expand this node according to attributes"
    self.expanded += 1
    if here.nodeType == here.ELEMENT_NODE:
      if 1:
        expr = here.getAttribute(self.namespace+'atts')
        if expr:
          atts = self.parseAtts(expr, data)
          self.atts(here, atts)
      
      # repeat
      if 1:
        expr = here.getAttribute(self.namespace+'repeat')
        if expr:
          name, repeat = self.parseRepeat(expr, data)
          self.repeat(here, data, name, repeat)

      # let (a single instance repeat)
      if 1:
        expr = here.getAttribute(self.namespace+'let')
        if expr:
          name, repeat = self.parseRepeat(expr, data)
          self.repeat(here, data, name, [repeat])
      	
      # if (a conditional repeat)
      if 1:
        expr = here.getAttribute(self.namespace+'if')
        if expr:
          iff = self.parseExpr(expr, data)
	  repeat = iff and [{}] or []
	  self.repeat(here, data, '__iff__', repeat)

      # replace
      if 1: 
        expr = here.getAttribute(self.namespace+'replace')
        if expr:
          replace = self.parseExpr(expr, data)
          c1 = len(gc.get_objects())
          self.replace(here, replace)
       
      # insert
      if 1:
        expr = here.getAttribute(self.namespace+'insert')
        if expr:
          insert = self.parseExpr(expr, data)
          c1 = len(gc.get_objects())
          self.insert(here, insert)

    for node in here.childNodes:
      try:
        self.expand(node, data)
      except KeyError:
        # because this loop occasionally iterates through
	# nodes that have been removed by a repeat clause
	# local replaces/inserts will raise key errors
	# so let's catch them here until we can iterate over a 
	# mutating list of childNodes
        #import sys
	#cls,ob,tb = sys.exc_info()
	#self.errors.append(`(cls.__name__,ob.args, tb.tb_lineno)`)
	#print "<!-- " , cls.__name__,ob.args, tb.tb_lineno , "-->"
        #del cls, ob, tb
        pass
    self.expanded -= 1


  def parseAtts(self, expr, data):
    "parse atts expression 'att1=exp1;att2=exp2;...' "
    pairs = [i.split('=',1) for i in expr.split(';')]
    #try:
      # our first 2.4 dependency...
      #data = dict([(k, self.parseExpr(expr, data)) for k,expr in pairs ])
    try:
      return dict((k, self.parseExpr(expr, data)) for k,expr in pairs)
    except:
      raise str("render.parseAtts(expr='%s')" % expr)
 
    #except:
      #print expr, data.keys()
    #  raise
    #return dict(data)
    
  def parseRepeat(self, expr, data):
    "parse repeat expr 'repeatvar=listexp' "
    name, exp = expr.split('=',1)
    try:
      return name, eval(exp, data)
    except NameError:
      #self.errors.append((exp,data.keys()))
      return name, '%s not found' % name      
      
  def parseExpr(self, expr, data):
    "parse an insert/replace expr"
    try:
      return eval(expr, data)
    except NameError:
      pass
      #raise 
      #self.errors.append((expr,data.keys()))  #### This and its like are the leak???
    except:
      self.trace = expr, data
      #print expr,data.keys()
      raise

  def atts(self, here, d={}):
    "update attributes here with data according to expr='att=datakey;'"
    #print "atts"
    here.removeAttribute(self.namespace+'atts')
    for k,v in d.items():
      if k.lower().strip() not in ('checked', 'selected','disabled') or v:
        here.setAttribute(k,str(v))
    
    
  def repeat(self, here, basedata, name, l=[]):
    "replace this node with a version rendered for each data item in l"
    #print "repeat"
    # allow for if and repeat and let tags
    try:
      here.removeAttribute(self.namespace+'repeat')
    except NotFoundErr:
      pass
    try:
      here.removeAttribute(self.namespace+'if')
    except NotFoundErr:
      pass
    try:
      here.removeAttribute(self.namespace+'let')
    except NotFoundErr:
      pass
    for item in l:
      node = here.cloneNode(deep=1)
      data = basedata.copy()
      data[name] = item
      try:
        self.expand(node, data)
      except:
        pass
        #print data.keys()
      here.parentNode.insertBefore(node, here)
    
    # dispose of here's child nodes, as the system will  
    # try to expand it whether it remains in the tree or not...
    for i in here.childNodes:
      here.removeChild(i)
    # then remove the template itself
    here.parentNode.removeChild(here)
    del here
    
  def node(self, here, x):
    "return a dom object, irrespective of data type"
    if x.__class__.__name__ in self.DOM_CLASSES:
      return x
    # this is not a dom node, so treat it as a string
    x = str(x)
    # preserve line breaks, except for pre and textarea tags
    if '\n' in x and here.localName.upper() not in 'PRE TEXTAREA':
      # enclose lines in <div>, separated by <br/>
      div = self.doc.createElement('div')
      # put a <br/> between each text node
      lines = sum(((self.doc.createTextNode(i), self.doc.createElement('br')) for i in x.split('\n')), ())[:-1]
      for line in lines:
        div.appendChild(line) 
      return div
    else:
      # we can return this as a plain text node
      return self.doc.createTextNode(x)

  def replace(self, here, x):
    "replace this node with x"
    #print "replace"
    try:
      here.removeAttribute(self.namespace+'replace')
    except NotFoundErr:
      pass
    node = self.node(here, x)
    here.parentNode.replaceChild(node, here)
    
  def insert(self, here, x):
    #print "insert"
    "replace the content of here with x"
    here.removeAttribute(self.namespace+'insert')
    node = self.node(here, x)
    for i in here.childNodes:
      here.removeChild(i)
    here.appendChild(node)
    
  def noteErrors(self):
    "append errors to end of document as comments"
    body = self.doc.getElementsByTagName('body')[0]
    for i in self.errors:
      #print i
      comment = self.doc.createComment(i)
      space = self.doc.createTextNode('\n  ')
      body.appendChild(space)
      body.appendChild(comment)
    space = self.doc.createTextNode('\n  ')
    body.appendChild(space)
    ####!!!!
    self.errors = []

########################################################
# TODO Give this class object context without breaking #
#      rendering mechanisms			       #
########################################################
class Form:
  "a callable, refreshable template for simple forms"
  def __init__(self, path):
    self.path = path
    self.refresh()
  def refresh(self):
    self.template = Render(self.path)
  def __call__(self, req):
    self.prepare(req)
    return self.template(self, req)
  def prepare(self, req):
     "make changes to req before rendering - to be subclassed"
     pass 

def test():
  global r
  filename = len(sys.argv)>1 and sys.argv[1] or 'eg.xml'

  class X:
    uid = 100
    text = 'hello some text here'
    somelist = [{'id':100,'name':'one hundred'}
      , {'id':200,'name':'two hundred'}
      , {'id':300,'name':'three hundred'}
      ]
    someotherlist = [{'name':'red'}, {'name':'yellow'}, {'name':'green'}]
    def fn(self,n): return "a result %d" % n
        
  ob = X()
  req = {'message':'tis a message'}  

  r = Render(filename)
  data = {'ob':ob, 'req':req}
  #print r(data, {'url':'sss'})
if __name__=='__main__': test()
