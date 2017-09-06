"""render evo links - [uid]  [url] [uid caption] [url caption]"""

from markdown import Extension
from markdown.util import etree
from markdown.inlinepatterns import Pattern


def safeint(s):
  ""
  try:
    return int(s)
  except:
    return 0


class EvoLinkExtension(Extension):

  def __init__(self, *args, **kwargs):
    ""
    super(EvoLinkExtension, self).__init__(*args, **kwargs)

  def extendMarkdown(self, md, md_globals):
    ""
    self.md = md

    EVOLINK_RE = r'\[(.*?)( .*?)?\]'
    evolinkPattern = EvoLinks(EVOLINK_RE, self.getConfigs())
    evolinkPattern.md = md
    md.inlinePatterns.add('evolink', evolinkPattern, "<not_strong")


class EvoLinks(Pattern):
  ""
  def __init__(self, pattern, config):
    ""
    super(EvoLinks, self).__init__(pattern)
    self.config = config

  def handleMatch(self, m):
    "return html for match"
    # before = m.group(1)
    target = m.group(2).strip()
    caption = (m.group(3) or '').strip()
    # after = m.group(4)

    # is target a valid page uid?
    try:
      page = self.md.req.user.Page.get(safeint(target))
      target = page.purl()
      caption = caption or page.name or target
      extra = {}
    except:
      # we assume an external url
      caption = caption or target
      extra = {'rel': 'nofollow'}
    a = etree.Element('a')
    a.text = caption
    a.set('href', target)
    for k, v in extra.items():
      a.set(k, v)
    return a

  def _getMeta(self):
    """ Return meta data or config data. """
    # TODO - needed?
