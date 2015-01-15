# -*- coding: utf-8 -*-

"""
config file for base.User

configuration value here act as defaults, so NO PARAMETER SHOULD BE REMOVED 
"""

from base.data.schema import *

# the following are likely to be overridden in an app's User/config.py 
registration_method="admin"  # options are: "self" : (the default) online self registration with email confirmation
                            #              "admin" : admin has to register every user 
                            #              "approve" : online self registration with approval by admin
user_email_required=False


class User(Schema):
  table='users'
  id=TAG,KEY
  pw=TAG
  email=TAG,KEY
  when=DATE,now
  stage=TAG,''
  insert=[
    dict(uid=1,id='guest',email='guest@versere.com',stage='verified'),
    dict(uid=2,id='admin',email='admin@versere.com',stage='verified'),
    ]

