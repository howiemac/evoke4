"""Basic XML Document Sanity Test
"""
from xml.sax import parse, ContentHandler, SAXParseException
from glob import glob as ls
import inspect
from cStringIO import StringIO

def logPoint(msg=''):
  stack = inspect.stack()
  print stack
  # remove the logPoint bit
  stack = stack[1:]
  stack.reverse()
  output = StringIO()
  if msg:
    output.write(str(msg)+'\n')
    for frame, filename, line, funcname, lines, unknown in stack:
      if filename.endswith('/unittest.py'):
        continue
#      if filename.startswith('./'):
#        filename = filename = filename[2:]
      output.write('%s:%s in %s:\n' % (filename,line,funcname))
      output.write('  %s\n' % ''.join(lines)[:-1])
    s = output.getvalue()
    return s    

for directory in ("xml",):
  for file in ls('../%s/*.xml' % directory):
    try:
      print file
      parse(file, ContentHandler())
    except:
      raise
      print logPoint('Error in %s' % file)

