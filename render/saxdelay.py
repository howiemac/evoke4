""" a delay line using pre-parsed sax events
"""
from xml.sax import ContentHandler

class OneEventDelay(ContentHandler):
  "pre-parse sax document then feed events to handler"
  def __init__(self):
    ""
    self.events = []
    self.index = 0

  def set_handler(self, handler):
    self.handler = handler
    self.handler.pre_parser = self
    self.handler.read_ahead = self.read_ahead

  def store(self, what, **kw):
    "store events"
    self.events.append((what, kw))

  def handle(self, event):
    "make our handler handle an event" 
    # this should handle iterators as gracefully as methods
    fname, kw = event
    fn = getattr(self.handler, fname)
    return fn(**kw)

  def read_ahead(self):
    "return next-event-but-one"
    index = self.index + 1
    if index < len(self.events):
      return self.events[index]
    else:
      return '', {}
      
  def next(self):
    "pass the next event to our handler"
    if self.index < len(self.events):
      res = self.handle(self.events[self.index])
      self.index += 1
      return res
    else:
      # reset the index for the next run through
      self.index = 0
      raise StopIteration

  def handler_read_ahead(self):
    "read event method for our handler"
    return self.pre_parser.read_ahead()

  # events
  def startDocument(self):
    ""
    self.store('startDocument')

  def startElement(self, tag, atts):
    ""
    self.store('startElement', tag=tag, atts=atts)

  def characters(self, content):
    ""
    self.store('characters', content=content)

  def endElement(self, tag):
    ""
    self.store('endElement', tag=tag)

  def endDocument(self):
    ""
    self.store('endDocument')

  # be an iterator
  def __iter__(self):
    return self

class GeneratingHandler(ContentHandler):
  "flow oriented handler"
  
  # events
  def startDocument(self):
    ""
    self.store('startDocument')

  def startElement(self, tag, atts):
    ""
    self.store('startElement', tag=tag, atts=atts)

  def characters(self, content):
    ""
    self.store('characters', content=content)

  def endElement(self, tag):
    ""
    self.store('endElement', tag=tag)

  def endDocument(self):
    ""
    self.store('endDocument')

#### TEST ####

class PrintingContentHandler(ContentHandler):
  "a content handler to print out events"
 
  def show(self, event, **kw):
    "show an event"
    print event, kw

  # events
  def startDocument(self):
    ""
    self.show('startDocument')

  def startElement(self, tag, atts):
    ""
    self.show('startElement', tag=tag, atts=atts)

  def characters(self, content):
    ""
    self.show('characters', content=content)

  def endElement(self, tag):
    ""
    self.show('endElement', tag=tag)

  def endDocument(self):
    ""
    self.show('endDocument')
    # flush out event queue here
    self.show('')
    self.show('')

if __name__=='__main__':
  from xml.sax import parse
  handler = PrintingContentHandler()
  pre = OneEventDelay(handler)
  parse('test.xml', pre)
