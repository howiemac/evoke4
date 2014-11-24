# -*- coding: utf-8 -*-

"""
config file for base.Reset  (used by base.User)
"""

from base.data.schema import *

class Reset(Schema):
  "password reset request"
  user = INT, 0
  expires = DATE
  key = TAG
  stage = TAG, ''

