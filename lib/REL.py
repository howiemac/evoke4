"""
This module implements the REL (REL) class, used for relational links between tables/objects

A schema definition of thing=REL causes an INT(11) to be added to the database, to store the uid of the related class Thing
On construction of an instance of REL, the link is stored as in integer. It is converted to the object it refers to when first accessed.

So: 
- when setting a REL attribute, you are dealing with a uid (ie an integer - this class). 
- when getting, you are dealing with an object of the class referred to. This object is cached for the lifespan of the instance.
- when flushing, the uid is flushed

e.g. in config.py or config_base.py: 

class = User(req)
  account=REL #creates an account column in a user table

and in use:

  user=self.User.get(5)
  user.account=8 
  print user.account.name #gives the name of account 8 
  user.flush() #flushes 8 to the account column in the user table
  return user.account.view(req)  #the account object remains cached
 
 
The magic is done in data.py ( __getattribute__ )

(Ian Howie Mackenzie - April 2007)
"""

from INT import INT


class REL(INT):
  """
  object relationships
  """

def test():
  pass

if __name__=='__main__': test()
