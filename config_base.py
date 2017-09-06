# -*- coding: utf-8 -*-

"""
config file for base items

used whether running single app or multi app

configuration value here act as defaults, so NO PARAMETER SHOULD BE REMOVED 
"""

from data.schema import *

#do NOT override these in other config files
evoke_version=4 # minor code version - do not play with this unless you are SURE you know what you are doing....
evoke_major_version=4 # do not change this - odd numbers are development, even numbers are stable

# the following are set in serve/app.py and can be used but not should not be overridden - they are here for information only:
# copyright= ... # this message is shown on the console log on startup
# app_filepath= ...
# base_filepath= ...
# htdocs_filepath= ...

# the following MUST be provided in an app's config.py or config_site.py
domains=["127.0.0.1"] # eg ['versere.com','www.versere.com']
domain='' #if not provided,  this is set to domains[0] by serve/app.py

# the following is typically overridden in base/config_site.py
connect='127.0.0.1 base 123456' #database connection parameters - normally only required here

# the following are likely to be overridden in an app's config.py or config_site.py
urlpath='/evoke'  # must have a preceding "/", or else be ""
urlhost='' #if not provided, this is set to 'http://'+self.Config.domain by serve/app.py - this assumes the system is running on port 80, as far as the outside world is concerned
sitename='' # if not given, hostname will generally be used

default_class=None # when supplied, enables urls of the form: domain/urlpath/12345 or (if not urlpath) domain/12345, which will call (the view() method of) uid 12345 for the default_class

mailto= 'mail@localhost' #contact email address
mailfrom= '' # email from address - if empty string or False, no emails will be sent
bugmailto= '' # email to address for bug email alerts - empty string means no emails will be sent
SMTPhost= '127.0.0.1' #email SMTP host - if empty string or False, no emails will be sent
SMTPlogin=() #email SMTP login, in form (<user>,<password>), if there is a login required

meta_description="evoke web application engine"
meta_keywords="evoke,web,application,engine,python,mysql,twisted"

# the following is typically overridden in the server folder site config, i.e. config_site.py (single app) or config_multi.py (app farm)
database='' #this will default to app name
port='8080' #for multiserve, this MUST be put in config_multi.py, to override any app settings

#the following applies only to base_multi.py, and MUST be set in base/config_multi.py
apps=[]

# Formatter - default to standard, may be overriden with 'markdown'
text_formatter = ''

#the following data schema may be subclassed or overidden in an app's config.py

class Var(Schema):
  table='vars'
  name=TAG,KEY
  value=INT
  textvalue=TAG
  datevalue=DATE
  comment=TAG
  insert=[dict(name='evoke-version',value=evoke_version,comment='used for patching')] # this entry is essential

 
# include config.py files from class folders
from Page.config import *  
from User.config import *  
from Session.config import *  
from Permit.config import *  
from Reset.config import * 
