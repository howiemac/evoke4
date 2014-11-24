""" Test DB.py in isolation.

    Call with twisted.trial eg.

      trial test_DB.py

    In the context of base, and by extension the rest of Evoke
    only init_db and execute are used by external functions.

    The aim of the current exercise is to maintain the current interface
    whilst rationalising code and introducing an asyncrous interface

"""
from twisted.trial import unittest
from twisted.internet.defer import inlineCallbacks  # , returnValue
from DB import DB, init_db, execute, aexecute

connect_config = ('', 'root', 'Elgar104')


class InitDBTestCase(unittest.TestCase):
  "test init_db including legacy connect_config formats"
  def setUp(self):
    ""

  def tearDown(self):
    ""

  def testTupleConnect(self):
    "connect using a tuple"
    init_db(connect_config)

  def testSpaceDelimitedConnect(self):
    "connect using a space delimited string"
    init_db(' '.join(connect_config))

  def testCommaDelimitedConnect(self):
    "connect using a space delimited string"
    init_db(','.join(connect_config))

  def testDBConnect(self):
    "connect by passing connect_config direct to DB object"
    DB(connect_config)


class ExecuteTestCase(unittest.TestCase):
  """ Not full coverage but the least that would
      possibly let us know that we have an execute
      connection that can handle substitutions.
  """
  def setUp(self):
    ""
    init_db(connect_config)
    # #### TODO create test table

  def tearDown(self):
    ""
    # #### TODO drop test table

  def testNothing(self):
    "do nothing except setUp and tearDown"

  def testCalculation(self):
    "run a simple calculation on the database"
    sql = 'select 2+3 as res'
    l = execute(sql)
    self.assertEqual(len(l), 1)
    self.assertEqual(l[0]['res'], 5)

  def testSubstitution(self):
    "run simple calculation on db with parameter substitution"
    l = execute('select %s+%s as res', args=(2, 3))
    self.assertEqual(len(l), 1)
    self.assertEqual(l[0]['res'], 5)

  def testInsert(self):
    "an INSERT should return its uid"
    # assumes existence of test.test table
    sql = "insert into test.test(thing) values ('')"
    n = execute(sql)
    self.assertEqual(type(n), long)


class AsyncExecuteTestCase(unittest.TestCase):
  """ Not full coverage but the least that would
      possibly let us know that we have an execute
      connection that can handle substitutions.

      Asyncrous edition
  """
  def setUp(self):
    ""
    init_db(connect_config)

  def tearDown(self):
    ""

  def testNothing(self):
    "do nothing except setUp and tearDown"

  def testCalculation(self):
    "run a simple calculation on the database"
    sql = 'select 2+3 as res'
    d = aexecute(sql)

    # test the results using a callback function
    def testCallback(l):
      self.assertEqual(len(l), 1)
      self.assertEqual(l[0]['res'], 5)

    d.addCallback(testCallback)

    # always return a deferred
    return d

  @inlineCallbacks
  def testInlineCallbackCalculation(self):
    """run a simple calculation on the database

       Same test as last time, but recast as
       an inlineCallback rather than with a
       callback function.
    """

    sql = 'select 2+3 as res'
    l = yield aexecute(sql)

    # test the results
    self.assertEqual(len(l), 1)
    self.assertEqual(l[0]['res'], 5)

  @inlineCallbacks
  def testInsert(self):
    "an INSERT should return its uid"
    # assumes existence of test.test table
    sql = "insert into test.test(thing) values ('')"
    n = yield aexecute(sql)
    self.assertEqual(type(n), long)
