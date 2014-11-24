# -*- coding: utf-8 -*-

"""
config file for base.Permit  
"""

from base.data.schema import *

# the following are likely to be overridden in an app's User/config.py 
guests=False # do guests have access by default? 
permits={'master':['be'],'user':['edit']} #basis of permit system
default_permits={} #default permits a new member gets

class Permit(Schema):
  table='permits'
  user=REL,KEY
  group=TAG
  task=TAG,'view'
  insert=[dict(user=2,group='master',task='be')]

