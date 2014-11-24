"""
Sax based simple template rendering system
"""
from xml.sax import parse, ContentHandler
from cStringIO import StringIO
import itertools

class RenderHandler(ContentHandler):
  """ This handler finds rendering events

      When a rendering  attribute is found in a startElement event
      a context is pushed onto the context stack.  
        This includes the rendering action, the current environment
        and the name of the tag, so endElement knows to remove the
        current context at the end of its scope.
      When outside a context, events are passed directly to output.
      While inside a context, output is determined according to the
      current rendering action.
 
        action		output
        atts		the start tag with updated attributes,
                        continue output as no context added
        if<-False	none
        if<-True	as per input (no context added)
        insert		<tag>[insert tag value]</tag>
        replace		[replace tag value]

        repeat		no output. Start recording incoming events.
 			When an equivalent end tag is found, 
			replay these events to a sub parser, adding
                        the current value of the repeat argument to
                        the environment
  """
  ATTS = set('if repeat let replace insert atts'.split())
  EMPTY = 'base meta link hr br basefont param img area input isindex col'.split()
  def __init__(self, env={}):
    ContentHandler.__init__(self)
    # output file
    self.out = StringIO()
    # stack of (action, environment, release tag) for each current context
    self.stack = [('', env, '')]
    # stack of (id, tag) for each tag. Used to match tags on self.stack
    self.tag_stack = []
    # flag when we are in a singleton tag
    # used by self.showStartElement(), self.showEndElement
    self.singleton = False

  def read_ahead(self,*a,**k):
    "dummy read ahead method"
    return '',''
    
  def pushTag(self,tag, count=[0]):
    "push a (uid,tag) pair to tag_stack, return uid"
    if tag==75:raise
    count[0] += 1
    self.tag_stack.append((count[0], tag))
    return count[0]

  def popTag(self,tag):
    "pop a tag, check the tag matches, return its uid"
    try:
      uid, tagname = self.tag_stack.pop()
    except IndexError:
      open('emptylist.txt', 'a').write(str(self.tag_stack)+"\n"+str(self.stack))
    assert tagname == tag
    return uid

  def startElement(self, tag, atts):
    ""
    # push tag to stack
    tagid = self.pushTag(tag)    
    # convert atts object to a conventional dictionary
    atts = dict(atts)
    keys = set(atts.keys()) 
    # retrieve our current context
    act, env, rtag = self.stack[-1]
    # if we are in a repeat tag, we just record this event
    if act=='repeat':
      self.repeat_events.append(('startElement', tag, atts))
      return
    if act=='let':
      self.repeat_events.append(('startElement', tag, atts))
      return
    # If there are no significant atts, we can show this tag and go on
    if not keys.intersection(self.ATTS):
      self.showStartElement(tag, atts)
      return
    # if the current act is if, then this is not included, so no more processing
    if act=='if':
      return

    for key in ('repeat','let'):
     if key in atts.keys():
      # while in the repeat tag, record sax events to a list
      # these will be replayed to another Handler instance for each
      # item in the repeat list
      # we need to store the value of repeat until endElement
      try:
        value = atts[key]
      except:
        print dict(atts)[key]
        raise
      self.repeat_name, self.repeat_data = self.parseRepeat(value, env)  
      if key=='let':
        self.repeat_data=[self.repeat_data]
      # reset the event list
      self.repeat_events = []
      # remove the repeat tag from atts to avoid infinite recursion
      atts = dict(atts)
      del atts[key]
      self.repeat_events.append(('startElement', tag, atts))
      self.stack.append((key, env, tagid))
      return
    # atts
    if 'atts' in keys:
      # parse and update atts
      d = self.parseAtts(atts['atts'], env)
      atts.update(dict(d))
      keys = set(atts.keys())

    # check for a new 'if' condition
    if 'if' in keys:
      value = eval(atts['if'], env)
      if not value:
        # hide output until matching end tag
        self.stack.append(('if', env, tagid))
        # no output required - we're done here
        return

    # check for replace
    if 'replace' in keys:
      value = str(eval(atts['replace'], env))
      if tag!='textarea':
        value=value.replace('\n','<br/>\n')
#      if value.__class__.__name__=='Element':
#        value=value.Toxml()
      # push our context to stack 
      self.stack.append(('replace', env, tagid))
      self.out.write(value)
   
    # check for insert if we're not already replaced
    if 'insert' in keys and 'replace' not in keys:
      try:
        value = str(eval(atts['insert'], env))
        if tag!='textarea':
          value=value.replace('\n','<br/>\n')
#        if value.__class__.__name__=='Element':
#          value=value.Toxml()
      except:
        print atts['insert']
        print env.keys()
        raise
      # show the start tag and the inserted content
      self.showStartElement(tag, atts)
      self.out.write(value)
      # push our context to stack
      self.stack.append(('insert', env, tagid))
      
    # we only need to show the tag now when we aren't in context
    if not act:
      self.showStartElement(tag, atts)

  def endElement(self, tag):
    ""
    # get tag id from tag_stack
    tagid = self.popTag(tag)
     
    act, env, rtagid = self.stack[-1]
    # if we are in a repeat tag, we just record this event
    if act in ('repeat','let'):
      self.repeat_events.append(('endElement', tag))

      # the following breaks if the current context contains
      # a repeat of the same tag.  We need a tag stack

      # check for the completion of this repeat section
      if tagid==rtagid:
        # render the repeats
        self.repeat(env)
        self.stack.pop()
      return
    # if this is not the current release tag, we need only show the tag
    if tagid!=rtagid: 
      self.showEndElement(tag)
      return
    # we are done with the current context
    self.stack.pop()
    if 'if' == act:
      pass 
    if 'repeat' == act:
      pass 
    if 'let' == act:
      pass 
    if 'replace' == act:
      pass
    if 'insert' == act:
      self.showEndElement(tag) 
    if 'atts' == act:
      pass
 
  def characters(self, content):
    ""
    act, env, rtag = self.stack[-1] 
    # if we are in a repeat tag, we just record this event
    if act in ('repeat','let'):
      self.repeat_events.append(('characters', content))
      return
    if not act:
      self.out.write(content) 

  def repeat(self, env):
    "render a repeating cycle by feeding events to sub-handlers"
    count = itertools.count()
    for i in self.repeat_data:
      # we need to recurse into another instance of ourselves
      # but we trigger the events by hand, rather than letting the sax parser do it
      env = dict(env)
      # we add some values to the env
      env[self.repeat_name] = i
      counter = count.next()
      # count and strobe always refer to the innermost loop
      env['count'] = counter
      env['strobe'] = counter % 2
      # but it would be dandy to have access to the outer loops
      env[self.repeat_name+'_count'] = counter
      env[self.repeat_name+'_strobe'] = counter % 2
      
      
      # here is that instance
      handler = self.__class__(env)
      # whitespace is used to keep the indentation right for repeats
      whitespace = ''.join([i[1] for i in self.repeat_events if i[0]=='characters' and not i[1].strip()][-2:])
      for eventtuple in self.repeat_events:
        fname = eventtuple[0]
        params = eventtuple[1:]
        # trigger the event
        fn = getattr(handler, fname)
        fn(*params)
        
      # repeat the last two whitespace events, which should be ('\n',indent)
      self.out.write(whitespace)
      self.out.write(handler.out.getvalue()) 
    self.repeat_data = []    

  def showStartElement(self, tag, atts):
    ""
    act, env, rtag = self.stack[-1] 
    if not act:
      # we need to use appropriate quote marks for each attribute, and to omit rendering tags
      pairs = ' '.join(('"' in i and "%s='%s'" or '%s="%s"') % i  for i in atts.items() if i[0] not in self.ATTS)
      gap = pairs and ' ' or ''
      # look ahead to the next event.  If it's an endElement
      # then we treat this tag as a singleton
      next_event,next_env = self.read_ahead()
      if next_event == 'endElement' and tag in self.EMPTY:
        self.singleton = True
        terminator = '/'
      else:
        terminator = ''
      s = '<%s%s%s%s>' % (tag, gap, pairs, terminator)
      self.out.write(s)
   
  def showEndElement(self, tag):
    ""
    act, env, rtag = self.stack[-1] 
    if not act:
      # singleton tags don't need endings
      if self.singleton:
        # reset the singleton flag
        self.singleton = False
      else:
        s = '</%s>' % tag
        self.out.write(s)
      s = '</%s>' % tag
      #self.out.write(s)

  def parseAtts(self, expr, env):
    "parse atts expression 'att1=exp1;att2=exp2;...' "
    # we allow semicolons escaped like... \;
    expr = str(expr).replace('\;', '~')
    pairs = tuple(i.replace('~',';').split('=',1) for i in expr.split(';'))
    try:
      res = dict((k, eval(expr, env)) for k,expr in pairs)
      if not res.get('selected',True):
        del res['selected']
      if not res.get('checked',True):
        del res['checked']
      if not res.get('disabled',True):
        del res['disabled']
      return res
    except:
      print 'parseAtts error'
      print expr
      #print env.keys()
      for act, env, tag in self.stack: print (act, tag)
      raise  

  def parseRepeat(self, expr, env):
    "parse repeat expr 'repeatvar=listexp' "
    name, exp = expr.split('=',1)
    try:
      return name, eval(exp, env)
    except NameError:
      return name, '%s not found' % name
      
  def endDocument(self):
    ""
    self.out.reset()
    #print self.out.getvalue()

if __name__=='__main__':
  h = RenderHandler()
  parse('test.xml', h) 
