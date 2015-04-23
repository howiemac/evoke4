"""
(Ian Howie Mackenzie / Christopher J Hurst)

get_apps() processes config files, and returns a dictionary of application class structures:

for each app, we
    - create a Config class for an app, from config*.py modules
    - set up application structure based on the Config object definitions (ie Schema subclasses)
    - call the database creation/maintenance code
    - mix together DataObject-esque classes

NOTE - a config.py definition overrides a config_base.py definition
     - a config_site.py definition overrides other definitions
     - config_multi.py overrides  config_site.py, but is only loaded for multiserve 
"""

from url import Url
from baseobject import Baseobject
from inspect import isclass
from os.path import lexists,split
from os import getcwd
from sys import modules
#from base.History import History
from base.data import  init_db, makeDataClass, schema
#from base.Flow import makeFlowClass
#from base.Select import makeSelectClass
from base.data import schema, patch

class App:

  db_started=False #class variable switch to ensure db connection is done only once

  def __init__(self,app=""):
    """get the configuration for this app
       the app parameter will have a value only when using multiserve
    """
    appname= app or split(split(getcwd())[0])[1]    
    app_fullpath = getcwd()
#    print ">>>>>>>>>>>>>>>>> APP ",appname
    self.app=app
    # get paths
    self.app_path=app and ("%s.code." % app) or ''
    if app: #multiserve
      self.app_filepath='../%s/code/' % app
      base_filepath=''  # i.e. base folder, where multiserve.py is called from
      htdocs_filepath='../%s/htdocs/' % app
    else: # single app
      self.app_filepath=''  # i.e. the app folder, where single serve.py is called from
      base_filepath='../../base/'
      htdocs_filepath='../htdocs/' 
#    print ">>>>>>>>>>>>>>>>> app filepath: ",self.app_filepath
#    print ">>>>>>>>>>>>>>>>> base filepath: ",base_filepath

    # build the schemaClasses and config dictionaries - siteconfig overrides config, which in turn overides baseconfig
    self.schemaClasses={}
    self.config=dict(app=app,app_filepath=self.app_filepath,base_filepath=base_filepath,htdocs_filepath=htdocs_filepath)
    self.get_config('config_base','base.')
    self.get_config('config_site','base.')
    self.get_config('config',self.app_path)
    self.get_config('config_site',self.app_path)
    if app: #we have multiserve...
      self.get_config('config_multi','base.')

#    print "SCHEMA======>"
#    for k,v in self.schemaClasses.items():
#      print ""
#      print k,": ",v.__dict__
#    print ""
#    print "====== END OF SCHEMA"  

    # convert self.config to a class
    self.Config=type("Config",(object,),self.config) 
    #add app name
    self.Config.appname=appname 
    # and path
    self.Config.app_fullpath = app_fullpath
    #make sure we have a database
    self.Config.database=self.Config.database or appname
    if not self.db_started: #now that we have connect parameters, start db if this is the first app...
      init_db(self.Config.connect)
      self.db_started=True
    # do any pre-schema patching
    patch.pre_schema(self) 

    # create the database, if it doesn't exist
    schema.create_database(self.Config.database)

    # create the objects...
    self.classes = {"Config":self.Config}
    self.make_objects(self.schemaClasses.items())

    #interlink classes and make them globally available
#    print "--------"
#    print self.classes.items()
#    print "--------"
    classes = self.classes.items()
    for targetid, targetcls in classes:
      if targetcls.__name__!='Config': 
        for sourceid, sourcecls in classes:
          if sourceid != targetid:	# don't do self-linkage   #### TODO - define why not?
 	    setattr(targetcls, sourceid, sourcecls)
      # make classes available in globals (mostly for interactive testing)
      globals()[targetid] = targetcls

    # add other convenient config items
    self.Config.domain=self.Config.domain or self.Config.domains[0] 
    self.Config.urlhost=self.Config.urlhost or 'http://'+self.Config.domain  # this assumes the system is running on port 80, as far as the outside world is concerned
    self.Config.copyright= """
EVOKE version %s.%06d
Copyright (C) 2014 Evoke Foundation
All rights reserved.
""" % (self.Config.evoke_major_version,int(self.Config.evoke_version))

    # do any post-schema patching
    patch.post_schema(self)

  def get_config(self,module,path):
    "extract the schema classes, and the config items from the config modules"
#    print "-----------",path+module
    try:
      config=__import__(path+module,globals(),locals(),'__main__')#import the module
      for k,v in config.__dict__.items():
        if k not in schema.__dict__:
          if isclass(v) and issubclass(v,schema.Schema):
            self.schemaClasses[k]=v
	  else:
	    self.config[k]=v
    except Exception,e: 
#      print "ERROR IN %s.py : " % (path+module,),e
      raise
      
  def make_objects(self,schemaClasses):
    ""
    tables={}
    for (k,c) in schemaClasses:
#      print "....object...",k,c.__name__
      c.table=getattr(c,'table',c.__name__.lower())
      tables[c.table]=(k,c) # duplicate table - ie a subclass - 
        # with same table name, will override the base class, 
        # so that only the subclass is added to the database
    # add each table to the database
    for (k,c) in tables.values():  
      c.build_database(self.Config.database)
      klass=c.__name__.capitalize()#force capitalisation for class / object names - consistent, and avoids naming conflicts with methods, keywords etc
      # look for the py file locally first, if not there then it must be in base
      if lexists(self.app_filepath+klass+'.py') or lexists(self.app_filepath+klass):#allow for py file or folder
        module=self.app_path+klass
      else:  
        module='base.'+klass
      self.make_object(k,module,klass,c) 
#      print k,':',self.classes[k],self.classes[k].____
   
  def make_object(self,id,module,klass,schemaClass):
    "builds the self.classes dictionary"
    # set up class bases
    bases = []
#    print ">>>>>>>>>>>>>>>>>>>",id,klass,module ,schemaClass._v_columns
    bases.append(getattr(__import__(module,globals(),locals(),klass),klass))  #yuk... but it works...for base.module.klass too
    if schemaClass._v_columns or schemaClass.table:  # DataObject
      bases.append(makeDataClass(schemaClass))
    bases.extend([Url,Baseobject]) #do these last so we can override their attributes and methods in the module class
    #make the object
    #print bases
    cls =self.classes[id] = type(str(id), tuple(bases), {})


    # trigger __class_init__ if it exists
    if hasattr(cls, '__class_init__'):
      cls.__class_init__()


#    #make the module appear app-specific, so pickle doesn't get confused between modules when we have multiple apps - DOESNT WORK :(
#    c=self.classes[id]
#    pymod=c.__module__
#    appmod=c.__module__+'.'+self.app
#    modules[appmod]=modules[pymod] #create a pseudo module
#    c.__module__=appmod #use it
#    print pymod,appmod,c.__module__,id

def get_apps(applist):
  "returns a dictionary of {domain:classlist} - this is called once only, on startup, by dispatch.py"
  apps={}    
  for a in applist or [""]:
#    print "APP:",a
    app=App(a)
    for d in app.Config.domains:
      apps[d]=app.classes
  return apps  

#if __name__=='__main__':
#  makeApp()
