""" Test permit.Condition
"""

import unittest
from permit import Condition


class Ob(object):
  "straw object"
  @Condition()
  def emptyCondition(self):
    "dummy function"


class TestCondition(unittest.TestCase):
  ""
  def setUp(self):
    ""
    self.ob = Ob()

  def tearDown(self):
    ""

  def testNothing(self):
    ""
    pass

  def testEmptyCondition(self):
    "permissive condition"
    c = Condition()
    self.assertTrue(c.check(self.ob))

  def testUnmatchedCondition(self):
    "condition not met - missing attribute"
    c = Condition(stage='published')
    self.assertFalse(c.check(self.ob))

  def testMismatchedCondition(self):
    "condition not met - missing attribute"
    c = Condition(stage='published')
    self.ob.stage = 'draft'
    self.assertFalse(c.check(self.ob))

  def testMatchedCondition(self):
    "condition not met"
    c = Condition(stage='published')
    self.ob.stage = 'published'
    self.assertTrue(c.check(self.ob))

  def testMultiUnmatchedCondition(self):
    "condition not met, multiple conditions"
    c = Condition(stage='published', other='no')
    self.assertFalse(c.check(self.ob))

  def testMultiMatchedCondition(self):
    "condition not met, multiple conditions"
    c = Condition(stage='published', other='no')
    self.ob.stage = 'published'
    self.ob.other = 'no'
    self.assertTrue(c.check(self.ob))

  def testEmptyIsin(self):
    "test empty isin clause"
    c = Condition(isin={})
    self.assertTrue(c.check(self.ob))

  def testEmptyIsinCategory(self):
    "empty isin items don't count"
    c = Condition(isin={'stage': []})
    self.assertTrue(c.check(self.ob))

  def testNonexistentIsinCategory(self):
    "isin attribute doesn't exist"
    c = Condition(isin={'stage': ['draft', 'published']})
    self.assertFalse(c.check(self.ob))

  def testUnmatchedIsinCategory(self):
    "isin attribute doesn't exist"
    c = Condition(isin={'stage': ['draft', 'published']})
    self.ob.stage = 'unpublished'
    self.assertFalse(c.check(self.ob))

  def testMatchedIsinCategory(self):
    "isin attribute doesn't exist"
    c = Condition(isin={'stage': ['draft', 'published']})
    self.ob.stage = 'published'
    self.assertTrue(c.check(self.ob))

  def testMultiUnmatchedIsinCondition(self):
    "condition not met, multiple conditions"
    c = Condition(isin={'stage': ['draft', 'published']}, other='no')
    self.ob.other = 'no'
    self.assertFalse(c.check(self.ob))

  def testMultiMatchedIsinCondition(self):
    "condition not met, multiple conditions"
    c = Condition(isin={'stage': ['draft', 'published']}, other='no')
    self.ob.stage = 'published'
    self.ob.other = 'no'
    self.assertTrue(c.check(self.ob))

  def testMultiMatchedIsinConditions(self):
    "condition not met, multiple conditions"
    c = Condition(isin={'stage': ['draft', 'published'],
                        'other': ['no', 'yes']})
    self.ob.stage = 'published'
    self.ob.other = 'no'
    self.assertTrue(c.check(self.ob))


class TestConditionDecorator(unittest.TestCase):
  ""
  def setUp(self):
    ""
    self.ob = Ob()

  def tearDown(self):
    ""

  def testNothing(self):
    ""
    pass

  def testConditionExists(self):
    "check condition function exists in method"
    fn = self.ob.emptyCondition.condition
    self.assertTrue(fn(self.ob))

if __name__ == '__main__':
  unittest.main()
