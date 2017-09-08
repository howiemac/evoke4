""" permit decorators
    -- need to be after @classmethod, but before @template  ala

    @classmethod
    @admin
    @template
    def blah(self, req):
      ""
      ...

   extend with @Condition to allow checks to be made on an
   object's state at base.serve.dispatch.doMethod time

   eg.

   @Condition(stage='published')
   def fn():
     ...

   or

   @Condition(isin=dict(stage=['draft', 'published']))
   def fn():
     ...

   to reflect the parameter patterns of base.data.list
"""


class Permit(object):
  "sets permit on a function"
  def __init__(self, perm):
    ""
    self.perm = perm

  def __call__(self, fn):
    ""
    fn.permit = self.perm
    return fn


class Condition(object):
  "sets a condition on a function"
  def __init__(self, *args, **keywords):
    "*args are ignored (for now) **keywords are conditions"
    self.args = args
    self.keywords = keywords
    self.isin = self.keywords.get('isin', {})
    if 'isin' in keywords:
      del self.keywords['isin']

  def check(self, ob):
    "tests whether the object matches self.keywords and self.isin"
    for k, v in self.keywords.items():
      if not hasattr(ob, k):
        # fail if keyword doesn't exist in ob
        return False
      if getattr(ob, k) != v:
        # fail if keyword doesn't match value in ob
        return False

    # test isin
    for k, v in self.isin.items():
      # ignore empty items
      if not v:
        continue
      # fail for nonexistent keywords
      if not hasattr(ob, k):
        return False
      # fail if unmatched
      if getattr(ob, k) not in v:
        return False

    # all keywords have been matched
    return True

  def __call__(self, fn):
    "apply condition to function"
    fn.condition = self.check
    return fn


class Conditionfn(object):
  ""
  def __init__(self, check):
    "check is a function expecting an object"
    self._check = check

  #### TODO make sure req and ob are passed to check ####

  def check(self, req, ob):
    ""
    return self._check(ob)

  def __call__(self, fn):
    "apply condition to function"
    fn.condition = self.check
    return fn

# testing

def admin(fn):
  ""
  return Permit('main.admin')(fn)

if __name__ == '__main__':
  @Permit('main.admin')
  def test():
    return test.permit
  assert test() == 'main.admin'
  print 'OK'
