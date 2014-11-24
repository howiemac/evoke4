"""
 patches application data automatically on startup, according to evoke version number

 - 2 stage process: pre_schema and post_schema, both called from app.py
 - 
"""

from DB import execute
from base.lib import Error,safeint

class InvalidDatabaseError(Error):
  'INVALID DATABASE: database "%s" exists but has no Var table and/or evoke-version entry'

def pre_schema_patch(version,config):
  ""
#  if version<1974:
#   do("rename table `%s`.accounts to `%s`.pages" % (config.database,config.database))
#  if version<1977:
#   do("drop table `%s`.transactions" % config.database)
#   do("drop table `%s`.contacts" % config.database)
#   do("alter table `%s`.users change column account page int default 1" % config.database)
#  if version<2001:
#   do("insert into `%s`.pages (parent,`group`,name,kind,who,lineage) values (1,4,'site','site',4,'.1.')" % config.database)
#  if version<2470: 
#   do("update `%s`.pages set kind='group' where kind='community'" % config.database) 
#   do("update `%s`.pages set parent=4 where uid>2 and kind='group'" % config.database) 
#  if version<2682:
#   do("update `%s`.pages set text='publish_filepath=~\n' where kind='site' and `group`=4" % config.database) # home site default filepath
#  if version<2709: 
#   do("update `%s`.pages set parent=4 where kind='site' and `group`=4 and parent=1 and name!='site'"% config.database) # front site belongs to admin
#  if version<2710:
#   do("update `%s`.pages i,`%s`.pages p set i.`group`=p.`group` where i.kind='image' and i.`group`=0 and p.uid=i.parent" % (config.database,config.database)) 
#  if version<2828: # make unicode compatible
#    do("alter database `%s` charset=utf8" % config.database)
#    for t in [t["Tables_in_%s" % config.database] for t in execute("show tables from `%s`" % config.database)]:
#      for (c,typ) in [(c["Field"],c["Type"]) for c in execute("show columns  from `%s`.`%s`" % (config.database,t))]:
#        if typ=='text':
#          do("alter table `%s`.`%s` modify column `%s` mediumtext" % (config.database,t,c))
#      do("alter table `%s`.`%s` convert to charset utf8" % (config.database,t))
  
def post_schema_patch(version,app):
  ""
#  if version<2199: # init user dates
#    for u in app.classes['User'].list(where='page>1'):
#      u.when=u.page.when
#      u.flush()
#  if version<2910: # fix article seqs
#    app.classes['Page'].patch_seq()
#    print 'PATCH: seq patched'
#  if version<2965: # fix site prefs
#    for p in app.classes["Page"].list(kind='site'):
#      p.prefs=p.text
#      p.text=''
#      p.flush()
#    print 'PATCH: site prefs patched'

def pre_schema(app):
  "database adjustments prior to loading the schema"
  global version
  print 'checking patches for "%s"' % app.Config.appname
  config=app.Config
  version=config.evoke_version 
  try:
    res=execute("select * from `%s`.vars where name='evoke-version'" % config.database)
  except: 
    if config.database in [x["Database"] for x in execute("show databases")]:
      print [x["Database"] for x in execute("show databases")]
      raise InvalidDatabaseError,(config.database,)  # we have an invalid database 
    else: # we have no database, so it will be created by schema
      return
  if not res: #initial patch - ie create var
    pre_schema_patch(0,config) 
    execute("insert into `%s`.vars (name,value,comment) values ('evoke-version',%s,'used for patching')" % (config.database,config.evoke_version))
    return
  version=res[0]['value']  
  if version<config.evoke_version:
    pre_schema_patch(version,config)
    #set the var textvalue to version number to indicate we are not finished - in case the schema process crashes (so we don't attempt the patch again - safety first!)
    execute("update `%s`.vars set value=%s,textvalue='%s' where name='evoke-version'" % (config.database,config.evoke_version,version)) # set the evoke-version (with no schema in place)

def post_schema(app):
  "database adjustments after the schema is loaded"
  global version
##  if hasattr(globals(),'version') and (version<app.Config.evoke_version):
  vars=app.classes['Var']
  got_version=vars.fetch('evoke-version')
  z=safeint(got_version.textvalue)
  if z: #if there was a crash after pre-schema patching, z will now contain the version number we were patching to, otherwise z will be 0 
    version=z #reset version to pre-crash version
  if (version<app.Config.evoke_version):
    post_schema_patch(version,app)
  set_version(app)

def set_version(app):
  "updates or adds the evoke-version - requires schema to be in place"   
  config=app.Config
  vars=app.classes['Var']
  version=vars.fetch('evoke-version')
  if not version.value:
    vars.add('evoke-version',config.evoke_version,textvalue='valid',datevalue='',comment='used for patching') #create version var, dated today
    print "PATCH:version is %s" % config.evoke_version
  elif version.value<config.evoke_version:
    vars.amend('evoke-version',config.evoke_version,textvalue='valid',datevalue='') #update version, text and date
    print "PATCH:version updated to %s" % config.evoke_version
  elif version.textvalue!='valid':
    vars.amend('evoke-version',textvalue='valid',datevalue='') #update text and date
    print "PATCH:version updated to %s" % config.evoke_version
  
def do(sql):
  execute(sql)
  print 'PATCH:'+sql  
