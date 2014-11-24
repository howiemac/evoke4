from xml.dom import Node

def doc_order_iter(node):
  yield node
  for child in node.childNodes:
    for cn in doc_order_iter(child):
      yield cn
      
def doc_order_iter_filter(node, filter_func):
  if filter_func(node):
    yield node
  for child in node.childNodes:
    for cn in doc_order_iter_filter(child, filter_func):
      yield cn
    
def get_elements_by_tag_name(node, name):
  return doc_order_iter_filter(node
    , lambda n: n.nodeType==Node.ELEMENT_NODE and n.nodeName==name)
    
def get_elements_by_tag_name_ns(node, ns, local):
  return doc_order_iter_filter(node
    , lambda n: n.nodeType==Node.ELEMENT_NODE 
      and n.localName==local
      and n.namespaceURI==ns)
    
def get_first_element_by_tag_name_ns(node,ns, local):
  get_elements_by_tag_name_ns(node,ns, local).next()
  
def string_value(node):
  text_nodes = doc_order_iter_filter(node, lambda n:n.nodeType==Node.TEXT_NODE)
  return u''.join()

def get_elements_by_id(node, id):
  return doc_order_iter_filter(node
    , lambda n: n.nodeType==Node.ELEMENT_NODE and n.getAttribute('id')==id)
