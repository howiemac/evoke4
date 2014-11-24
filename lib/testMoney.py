""" Test change string-to-money change in MONEY.py
"""
from MONEY import MONEY

import unittest


class TestMoney(unittest.TestCase):
  ""
  def setUp(self):
    ""

  def tearDown(self):
    ""

  def testZero(self):
    ""
    self.assertEqual(MONEY('0'), MONEY(0))

  def testWholeNumber(self):
    "old version of MONEY didn't handle whole numbers"
    self.assertEqual(MONEY('1'), MONEY('1.00'))


if __name__ == '__main__':
  unittest.main()
