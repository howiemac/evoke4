""" mix-in class for evoke objects
"""

class Baseobject(object):
  ""

  def permitted(self, user):
    """ 
    for sub-classing
    
    user.can(self,what), when 'what' is a method, checks this method before checking the user permits.
    So, do not use user.can(method) in a `permitted()` method definition, or you will get infinite recursion!
    It is ok to use the user.can(permit) form - indeed this is why the `user` parameter is provided!
    
    """
    return 1
    

if __name__=='__main__':
  pass