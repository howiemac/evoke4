""" var object 

this is for storing system variables
"""

class Var(object):

  @classmethod
  def fetch(cls,name):
    "fetch var with given name"
    return cls.list(name=name)[0]

  @classmethod
  def next(cls,name,advance=True):
    "give (and, if advance, then increment) a counter variable"
    v=cls.fetch(name)
    next=v.value
    if advance:
      v.value=next+1
      v.flush()         
    return next

  @classmethod
  def add(cls,name,value=0,textvalue='',datevalue=None,comment=''):
    "add a new var of given name with given values"
    v=cls.new()
    v.name=name
    v.value=value
    v.textvalue=textvalue
    v.datevalue=datevalue
    v.comment=comment
    v.flush()    

  @classmethod
  def amend(cls,name,value=None,textvalue=None,datevalue=None,comment=None):
    "update var of given name with given values"
    v=cls.fetch(name)
    if value is not None:
      v.value=value
    if textvalue is not None:
      v.textvalue=textvalue
    if datevalue is not None:
      v.datevalue=datevalue
    if comment is not None:
      v.comment=comment
    v.flush()    

  @classmethod
  def say(cls,name):
    v=cls.fetch(name)
    return "%s : %s (%s) (%s) %s" % (v.name,v.value,v.textvalue,v.datevalue,v.comment)


