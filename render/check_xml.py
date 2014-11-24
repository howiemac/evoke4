from glob import glob as ls
from xml.sax import parse, ContentHandler
def check_xml():
  for directory in ("xml",):
    for file in ls('../%s/*.xml' % directory):
      try:
        print file
        parse(file, ContentHandler())
      except:
        raise
if __name__=='__main__': check_xml()
