from re import compile as RX
import itertools  

class Parser:  

  URI_TYPES = (  ('export' ,	RX('/(.*?)/([0-9]*?)/(.*?\.eve)$'))
                , ('obj',      RX('/()([0-9]+?)/(.*?)$'))                                                                                 
                , ('obj',      RX('/()([0-9]+?)()$'))                                                                                     
                , ('obj',	RX('/(.+?)/([0-9]+?)/(.*?)$'))
                , ('obj',	RX('/(.+?)/([0-9]+?)()$'))
                , ('namedobj',  RX('/(.+?)/([a-zA-Z0-9\-]+?)/(.*?)$'))
    		, ('cls' ,	RX('/(.+?)/()(.*?)$'))
    		, ('obj' ,	RX('/()()(.+?)$'))
                , ('default', 	RX('/()()()$'))
                  )
  
  def parseUri(self, uri):
    "return (uri_type, class, uid, method) for this uri"
    # create an iterator to find the first matching uri type
    type_comparison = ((name, rx.match(uri)) for name, rx in self.URI_TYPES)    
    type_match = itertools.dropwhile(lambda x: not x[1], type_comparison)
    try:
      uri_type, groups = type_match.next()
    except StopIteration:
      # this is an unknown uri
      return None, None, None, None
    # return 4-tuples of values according to uri_type
    # values should always be a 3-tuple
    values = groups.groups()
    #print uri_type, values
    return (uri_type,) + values

def test():
  ""
  p=Parser()

  # export
  uri="/page/345/345.eve"
  uri_type, cls, uid, method = p.parseUri(uri)
#  print uri
#  print "type:",uri_type," class:", cls, " uid:",uid, " method:",method
  assert uri_type=="export" and cls=="page" and uid=="345" and  method== "345.eve"

  # obj 1
  uri="/3/links"
  uri_type, cls, uid, method = p.parseUri(uri)
#  print uri
#  print "type:",uri_type," class:", cls, " uid:",uid, " method:",method
  assert uri_type=="obj" and cls=="" and uid=="3" and  method== "links"

  # obj 2
  uri="/3"
  uri_type, cls, uid, method = p.parseUri(uri)
#  print uri
#  print "type:",uri_type," class:", cls, " uid:",uid, " method:",method
  assert uri_type=="obj" and cls=="" and uid=="3" and  method== ""

  # obj 3
  uri="/user/3/links"
  uri_type, cls, uid, method = p.parseUri(uri)
#  print uri
#  print "type:",uri_type," class:", cls, " uid:",uid, " method:",method
  assert uri_type=="obj" and cls=="user" and uid=="3" and  method== "links"

  # obj 4
  uri="/user/3"
  uri_type, cls, uid, method = p.parseUri(uri)
#  print uri
#  print "type:",uri_type," class:", cls, " uid:",uid, " method:",method
  assert uri_type=="obj" and cls=="user" and uid=="3" and  method== ""

  # namedobj
  uri="/page/namedobj/view"
  uri_type, cls, uid, method = p.parseUri(uri)
#  print uri
#  print "type:",uri_type," class:", cls, " uid:",uid, " method:",method
  assert uri_type=="namedobj" and cls=="page" and uid=="namedobj" and  method== "view"

  # cls
  uri="/user/clsmethod"
  uri_type, cls, uid, method = p.parseUri(uri)
#  print uri
#  print "type:",uri_type," class:", cls, " uid:",uid, " method:",method
  assert uri_type=="cls" and cls=="user" and uid=="" and  method== "clsmethod"

  # obj 5
  uri="/welcome"
  uri_type, cls, uid, method = p.parseUri(uri)
#  print uri
#  print "type:",uri_type," class:", cls, " uid:",uid, " method:",method
  assert uri_type=="obj" and cls=="" and uid=="" and  method== "welcome"

  # default
  uri="/"
  uri_type, cls, uid, method = p.parseUri(uri)
#  print uri
#  print "type:",uri_type," class:", cls, " uid:",uid, " method:",method
  assert uri_type=="default" and cls=="" and uid=="" and  method== ""



if __name__=='__main__':
  test()


