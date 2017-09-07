"""
This module implements the TEXT class (a.k.a. TEXT), used for transient storage and manipulation of strings in the special Evoke text format.

O/S Currently assumes that Page.py is in use....

implements self.formatted() and self.summarised()

"""

import library as lib
from STR import STR
import urllib, re
from markdown import Markdown
from evolinks import EvoLinkExtension
from html2text import html2text


def markdown(text, req, *a, **k):
    ""
    extensions = k.setdefault('extensions', [])
    extensions.append(EvoLinkExtension())
    md = Markdown(*a, **k)
    md.req = req
    return md.convert(text)


class TEXT(STR):
    """
  Evoke text format handling
  """
    # re for url matching
    punct_pattern = re.escape(r'''"\'}]|:,.)?!''')
    url_pattern = r'http|https|ftp|nntp|news|mailto|telnet|file|irc|'
    url_rule = re.compile(
        r'%(url_guard)s(%(url)s)\:([^\s\<%(punct)s]|([%(punct)s][^\s\<%(punct)s]))+'
        % {
            'url_guard': r'(^|(?<!\w|"))',
            'url': url_pattern,
            'punct': punct_pattern,
        })

    # re for parsing
    replace_items = [
        ("<", "&lt;"), (">", "&gt;"), (" - ", " &ndash; ")
    ]  # don't want < in output as it causes text to be skipped by the browser
    replaces = dict(replace_items)
    replace_rule = re.compile(r'|'.join(map(re.escape, replaces.keys())))
    link_rule = re.compile(r'(\[)(.*?)(\])')
    pre_rule = re.compile(r'({{{)(.*?)(}}})|({{)(.*?)(}})|({)(.*?)(})',
                          re.DOTALL)
    pre_token = re.compile(r'{}')
    blockquote_rule = re.compile(
        r'(&lt;\n)(.*?)(\n&gt;)|(&lt;\n)(.*?)($)',
        re.DOTALL)  #note: this doesn't work with re.MULTILINE
    quote_rule = re.compile(
        r'(&lt;)(.*?)(&gt;)|(^&gt;)(.*?)($)',
        re.DOTALL + re.MULTILINE)  #note:  this needs re.MULTILINE
    image_rule = re.compile(r'(\[IMG )(.*?)(\])')
    table_rule = re.compile(r'(\[TABLE )(.*?)(\])')
    underline_pattern = r'(^| ])(_+%*]+)([^~^_+%* \n][^ \n]*)'
    # styles joined by underlines or other style symbols
    style_rule = re.compile(
        r'(^| )([~^_+%*]+)([^~^_+%* \n][^ \n]*)( [?.,;?!][ /n]|)',
        re.MULTILINE)
    # styles with closing tags
    linestyle_rule = re.compile(r'(^| )([~^_+%*)]+ )(.*?)(\n| [~^_+%*]+[\n ])',
                                re.MULTILINE)
    styles = {
        '~': '<i>%s</i>',
        '^': '<b>%s</b>',
        '_': '<u>%s</u>',
        '+': '<big>%s</big>',
        '%': '<small>%s</small>',
        '*': '<strong>%s</strong>',
        ')': '<center>%s</center>'
    }
    headerstyles = {
        '==': '<h3>%s</h3>',
        '--': '<h4>%s</h4>',
        '++': '<h5>%s</h5>',
        '__': '<h6>%s</h6>'
    }
    section_rule = re.compile(r'(.*\n)(\*\*+)( *\n)', re.MULTILINE)
    #  list_rule=re.compile(r'(^ *)([-#])(.*)')
    list_rule = re.compile(r'(^ *)([-#]|&ndash;)(.*)')

    # auto-sectioning into child pages (should be in page.py) ###################
    def sectioned(self):
        "splits ** headers into sections - e.g. called by Page.py when saving text"

        def subStyle(match):
            g = match.groups()
            #      return str(g)
            return '**%s' % g[0]

        pre = []

        def pushPre(match):
            "keep the braces as well as the contents"
            g = match.groups()
            pre.append((g[1] and g[0] + g[1] + g[2])
                       or (g[4] and g[3] + g[4] + g[5])
                       or (g[7] and g[6] + g[7] + g[8]))
            return '{}'

        def popPre(match):
            "reinstate the braces and content"
            return pre.pop(0)

        #start of sectioned
        if self:
            # get the text to process
            text = self
            # extract the pre-formatted text and replace with a {} token
            text = self.pre_rule.sub(pushPre, text)
            # extract the new sections and replace with a ** token
            text = self.section_rule.sub(subStyle, text)
            # split the sections based on the tokens
            sections = []
            for s in text.split('\n**'):
                #replace the pre-formatted tokens with the original text
                sections.append(self.pre_token.sub(popPre, s))
            return sections
        else:
            return [self]

    # processing for export (should be in page.py) ####################
    def exported(self, req):
        """ expands links and returns export-ready text
    O/S - this function is currently specific to Page.py..... SHOULD NOT BE IN HERE....
    """

        def expandlink(match):
            """expand page-uid links and other local links to full urls"""
            source = match.groups()[1].strip()
            if self.url_rule.search(source):
                return "[%s]" % source  # no change
            else:  # we have [page] or [page caption] or [local-url] or [local-url caption]
                z = source.split(' ', 1)
                url = z[0]
                caption = len(z) == 2 and (" " + z[1]) or " "
                try:
                    page = req.user.Page.get(int(url))
                    fullurl = page.full_url()
                except:
                    if lib.safeint(url):  # broken link
                        fullurl = "0"
                    else:  # local url, hopefully..
                        fullurl = req.user.external_url(url)
                return "[%s%s]" % (fullurl, caption)

        pre = []

        def pushPre(match):
            "keep the braces as well as the contents"
            g = match.groups()
            pre.append((g[1] and g[0] + g[1] + g[2])
                       or (g[4] and g[3] + g[4] + g[5])
                       or (g[7] and g[6] + g[7] + g[8]))
            return '{}'

        def popPre(match):
            "reinstate the braces and content"
            return pre.pop(0)

        #start of exported
        if self:
            # get the text to process
            text = self
            # extract the pre-formatted text and replace with a token
            text = self.pre_rule.sub(pushPre, text)
            # expand the links
            text = self.link_rule.sub(expandlink, text)
            #replace the pre-formatted tokens with the original text
            text = self.pre_token.sub(popPre, text)
            return text
        else:
            return ""

    # text formatting ##########################################3
    def formatted(self, req, chars=0, lines=0):
        "formats self for display"

        # check for override:
        # Substitute TEXT.markdown for TEXT.format if specified in config
        print (req.Config)
        if getattr(req.Config, 'text_formatter', '') == 'markdown':
            return self.markdown(req, chars, lines)

        def link(title, url, external=False):
            return '<a href="%s" %s>%s</a>' % (
                url, external and 'target="_blank"' or '', title)

        def headerstyle(line, style):
            return self.headerstyles[style] % line[:-1]  #strip the line feed

        def subHilit(match):
            "puts in highlighting of search terms"
            return '<em>%s</em>' % match.group()

        def subcode(source):
            return '<pre>%s</pre>' % source

        def sublink(match):
            """deal with [page-uid] or [url] or [page-uid caption] or [url caption]
         O/S - SPECIFIC to Page.py - SHOULD NOT BE IN base ???
         ugly stuff - maybe could be done better with more use of regex, methinks....
         BUT it does work and is clever enough....
         urls matched here will not be matched subsequently because they will be have been enclosed in parenthesis by link()
      """
            source = match.groups()[1].strip()
            match = self.url_rule.search(source)
            if match:  # we have [url] or [url caption]
                url = match.group()
                caption = source[match.end():] or url
                return _subURL(caption, url)
            else:  # we have [page] or [page caption] or [local-url] or [local-url caption]
                z = source.split(' ', 1)
                url = z[0]
                caption = len(z) == 2 and z[1] or ""
                try:  #is url a uid?
                    page = req.user.Page.get(int(url))
                    return link(caption or page.name or page.code, page.url())
                except:
                    if lib.safeint(url):  # its an invalid uid
                        return '<span class="broken">%s</span>' % (
                            caption or ('[%s]' % source, ))
                    else:  # its a local url, hopefully..
                        return link(caption or url, url)

        def _subURL(source, url=''):
            return link(
                source.replace("mailto:", ""), url or source, external=True)

        def subURL(match):
            return _subURL(match.group())

        def subBlockquote(match):
            g = match.groups()
            return '<blockquote class="evoke">%s</blockquote>' % (
                g[1] or g[4], )

        def subQuote(match):
            g = match.groups()
            if g[1]:
                return '<q>%s</q>' % g[1]
            else:  # must be g[4] - these are done in this rule as they need re.MULTILINE
                return '<blockquote class="evoke">\n%s</blockquote>' % g[4]

        def subStyle(match):
            g = match.groups()
            ops = reversed(g[1].strip())
            text = g[2].replace('_', ' ')
            for op in ops:
                text = self.styles[op] % text.replace(op, ' ')
            stop = g[3][1:]  # final punctuation ? remove leading space..
            return g[0] + text + stop

        def subLinestyle(match):
            g = match.groups()
            ops = reversed(g[1].strip())
            text = g[2]
            for op in ops:
                text = self.styles[op] % text
            return g[0] + text + g[3][-1]

        def subReplace(match):
            return self.replaces[match.group()]

        def listType(line):
            match = self.list_rule.match(line)
            return match and (
                ((match.group(2) == '#') and 'o' or 'u'),
                len(match.group(1)) + 1, match.group(3)) or ('', 0, '')

        # pre-formatted -------------------
        pre = []

        def pushPre(match):
            "keep the content within the braces, ditch the braces"
            g = match.groups()
            #      print "GROUPS",g
            pre.append(g[1] or g[4] or g[7])
            return '{}'

        def popPre(match):
            "reinstate the content, processed for display"
            t = pre.pop(0).replace('&', '&amp;').replace('<', '&lt;').replace(
                '>', '&gt;')  #display nested html and entities as raw text
            return (t.find('\n', 1) > -1 and '<pre>%s</pre>'
                    or '<tt>%s</tt>') % t.strip('\n\r')

        # format by line -------------------

        def format_line(line, result):
            # headers
            if line:
                style = nextline[:2]
                if style in self.headerstyles:
                    line = headerstyle(line, style)
                if line[:2] in self.headerstyles:  #ditch the style line
                    return
            # lists
            list, level, text = listType(line)
            l = "<%sl>" % list
            prev = result and result[-1][:4]
            if prev != l and (prev == '<ul>'
                              or prev == '<ol>'):  #finish previous list
                result[-1] += ('</' + prev[1:]) * self.listlevel
            if list:
                line = "<li>%s</li>" % text
                if prev != l:  # new list
                    self.listlevel = level
                    line = (l * level) + line
                else:
                    inc = level - self.listlevel
                    ll = inc < 0 and ("</%sl>" % list) * -inc or l * inc
                    result[-1] += ll + line
                    self.listlevel = level
                    return
            if line:
                # tables
                if line[0] == '|':
                    if prevline[:1] != '|':
                        result.append("<table>")
                    result[-1] += "<tr><td>%s</td></tr>%s" % (
                        line[1:].replace('|', '</td><td>'),
                        nextline[:1] != '|' and "</table>" or "")
                    return
#        # paragraphs
#        elif line[0]==' ':
#          line='<p>%s</p>' % line[1:-1]
# append to result (converting linefeeds "<br/>" tags)
            result.append(
                line.replace('<blockquote>\n', '<blockquote>').replace(
                    '\n', '<br/>'))

        #start of formatted
        self.has_more = False
        if self:
            # first deal with HTML
            if self.lstrip().startswith(":HTML"):
                #  HTML truncation produces broken pages, so we simply refuse to do it for now .....
                #        if chars: #
                #          self.has_more=chars<len(self)
                #          return self[5:chars+5]
                #        else:
                return self[5:]
            # get the text to process (with an extra linefeed to avoid end-of-file glitches)
            if chars:
                self.has_more = chars < len(self)
                text = self[:chars]
                if lines:  #normally, the lines restriction will not take effect (due to chars restrictions- only where lines are short, eg poetry
                    z = text.splitlines()
                    textlines = z[:lines]
                    text = "\n".join(textlines) + '\n'
                    self.has_more = self.has_more or (lines < len(z))
            else:
                text = self + '\n'
            #extract the pre-formatted text and replace with a token
            text = self.pre_rule.sub(pushPre, text)
            #replaces (eg replace angle brackets with html entities)
            text = self.replace_rule.sub(subReplace, text)
            #handle quotes and links and styles
            text = self.blockquote_rule.sub(subBlockquote, text)
            text = self.quote_rule.sub(subQuote, text)
            text = self.link_rule.sub(sublink, text)
            text = self.url_rule.sub(subURL, text)
            text = self.style_rule.sub(subStyle, text)
            text = self.linestyle_rule.sub(subLinestyle, text)
            # hilite the search terms
            hilite_terms = req.get('searchfor', '').split()
            if hilite_terms:
                text = re.compile(r'|'.join(map(re.escape, hilite_terms))).sub(
                    subHilit, text)
            #process the lines
            textlines = text.splitlines(True)
            result = []
            prevline = line = ''
            for nextline in (textlines + ['\n', '\n']):
                format_line(line, result)
                prevline = line
                line = nextline
#        print result[-1]
            format_line(line, result)
            #      print result[-1]
            text = "\n".join(result[1:])
            #      print text
            #replace the pre-formatted tokens with the text
            text = self.pre_token.sub(popPre, text)
            #fix glitches in  summarised text
            if chars or lines:
                text = text.replace("&lt;", '"')

#      return text.rstrip('\n').replace('<blockquote>\n','<blockquote>').replace('\n','<br/>\n')
            return text.rstrip('\n')
        else:
            return ""

    def summarised(self, req, chars=250, lines=3, formatted=True):
        " return summary of formatted text "
        if formatted:
            return self.formatted(req, chars, lines)
        # not formatted - ignore "lines"
        return self[:chars]

    def markdown(self, req, chars=0, lines=0):
        "delegate to Markdown"
        self.has_more = False
        # get the text to process
        text = self
        if chars:
            self.has_more = chars < len(self)
            text = self[:chars]
        if lines:
            z = text.splitlines()
            textlines = z[:lines]
            text = "\n".join(textlines) + '\n'
            self.has_more = self.has_more or (lines < len(z))

        def subimage(match):
            "render a [IMG (uid|url) attributes?]"
            source = match.groups()[1]
#            print match.groups()
            if ' ' in source:
                url, atts = source.split(' ', 1)
            else:
                url, atts = source, ''

            # check for a valid uid
            if lib.safeint(url):
                try:
                    img = req.user.Page.get(lib.safeint(url))
                    url = img.image_or_thumb_url()
                except:
                    raise
                    pass

            return '<img src="%s" %s />' % (url, atts)

        def subtable(match):
            "substitute a table object"
            source = match.groups()[1]
            # check for a valid uid
            if lib.safeint(source):
                table = req.user.Page.override_get(lib.safeint(source))
                return "<div class='display-table'>%s</div>" % (
                    table.text.replace('\n', ' '))
            else:
                return 'TABLE ERROR %s' % str(source)

        text = self.image_rule.sub(subimage, text)
        text = self.table_rule.sub(subtable, text)

        return markdown(text, req)

    def to_markdown(self, req):
        """Render to html using formatter, then use html2text to convert to Markdown"""
        html = self.formatted(req)
        md = html2text(html)
        # arguably we should convert links to [url caption] rather than
        # [url](caption) but since this method is intended to convert
        # legacy text in bulk the effort and potential for corner cases
        # suggests we should leave them as they are.

        return md


def test():
    t = TEXT('line one\nline two\nthird line\n\nhttp://deepserver.net')
    print t.sql()
    print t.formatted({'searchfor': 'one'})
    print isinstance(t, TEXT)


if __name__ == '__main__': test()
