""" parse xml to evo

TODO:  class atts --> cls

"""
from xml.sax import parseString, ContentHandler

class X2EHandler(ContentHandler):
  ""
  def __init__(self, *a, **k):
    ""
    ContentHandler.__init__(self, *a, **k)
    self.indent = 0     # indent level
    self.lines = []     # lines in evoke file

  def startElement(self, tag, args):
    ""
    phrase = ""
    gap = "  " * self.indent
    tag = tag.lower()
    # this is a naive implementation - need to handle
    # repeat, insert, replace with more sophistication
#    if 'replace' in args:
#      phrase = args["replace"].replace('ob.', 'self.')
#      self.lines.append("%s%s" % (gap, phrase))
#      return
#    if 'insert' in args:
#      phrase = args['insert'].replace('ob.', 'self.')
    # replace class with cls (until more classes need the name)
    # TODO handle content-type as content_type
    pairs = ', '.join(['%s="%s"' % (k.lower().replace('class', 'cls'), v.replace('"', '\"')) for k,v in args.items() if k not in ('insert', 'replace', 'atts')])
    self.lines.append("%s%s: %s" % (gap, tag, pairs))
    self.indent += 1
    if phrase:
      gap = "  " * self.indent
      self.lines.append("%s%s" % (gap, phrase))

  def endElement(self, tag):
    ""
    self.indent -= 1

  def endDocument(self):
    ""
    self.out = "\n".join([i for i in self.lines if i.strip()])

  def characters(self, s):
    ""
    gap = "  " * self.indent
    chars = s.replace('"', '\"')
    if s.strip():
      self.lines.append("%s\"\"\"%s\"\"\"" % (gap, chars)) 

def parse(s):
  "parse xml to evo"
  h = X2EHandler()
  parseString(s, h)
  return h.out 

if __name__=='__main__':
  import sys
  s = open(sys.argv[1]).read()
  open(sys.argv[2], 'wb').write(parse(s.encode('ascii','xmlcharrefreplace')))
