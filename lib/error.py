""" Error Base Class (cjh)
"""
class Error(Exception):
  "Base error class, prints it's own __doc__ string"
  def __init__(self, *kw, **args):
    self.msg = self.__doc__ % kw
  def __repr__(self):
    return self.msg
  def __str__(self):
    return self.msg

class TODO(Error):
  "%s has yet to be implemented"