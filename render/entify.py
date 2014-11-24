"""
hide html entities during processing
"""

import re

delims = '&%s;', '[[%s]]'
rxs = [re.compile(i % '(#?[A-Za-z0-9]*?)') for i in ['&%s;', '\[\[%s\]\]']]

def recode(s, delim, rx):
  ""
  def subst(match):
    return delim % match.groups()[0]
  return rx.sub(subst, s)

def decode(s):
  ""
  return recode(s, delims[0], rxs[1])

def encode(s):
  ""
  return recode(s, delims[1], rxs[0])

if __name__=='__main__':
  s = '<xml>  &nbsp;  &#123;  &gt;  &</xml>'
  s1 = encode(s)
  s2 = decode(s1)
  print s
  print s1
  print s2
