
class RemoteSQLDataObject(MassProducedSQLDataObject):
  "a data object that will flush changes to queue for remote transmission"
  TRANSMISSION_DIR = '/evoke/var/tx'

  def flatten(self, d):
    "flatten out our datetime objects for marshal"
    for k in d:
      if type(d[k]) is datetime:
        d[k] = `d[k]`

  def all_change(self):
    "mark all fields as changed where their value is not None"
    changed = dict((i, True) for i in self._v_fields if getattr(self, i) is not None)
    self._v_changed.update(changed)

  def flush(self, only=[], remote=True):
    "save changes to db, filtered by only"
    changes = DataObject.flush(self, only=only)
    if not changes:
      return
    fields = self.quoted_pairs(changes.items())
    sql = "update %s set %s where uid=%d" % (self.table, fields, self.uid)
    try:
      execute(sql)
    except:
      print sql
      raise
    if remote and hasattr(self, 'sendable'):
      if self.sendable():
        Flush(self.TRANSMISSION_DIR).flush((self.__class__.__name__, self.uid, changes)) 

  #### FIXME the following two methods need to be
  #### ultra secure, possibly on a local socket rather
  #### than on the main tcp/ip handler
  
  @classmethod  
  def remote_update(cls, req):
    "update and acknowlege - for updates from remote db"
#    open('/tmp/waa.txt','w').write('remote_update')
#    def log(s):
#      open('/tmp/remote_update.log','a').write(s+'\n')
    #if req['request']['REMOTE_ADDR'] != '127.0.0.1':
    if req['request'].getClientIP() != '127.0.0.1':
#      log('remote request?!')
      raise 'local requests only!'
#    log('local request')
    args = cls.typecast(req)
    uid = int(args['uid'])
    del args['uid']
    existing = False
    try:
      ob = cls.get(uid)
      existing = True
    except RecordNotFoundError:
      ob = cls.remote_new(uid)
    ob.update(args)
    ob.flush(remote=False)
 #   log('flushed')
    if existing:
#      ob.logEvent('remote', 'updated', `args`) #testing 
      if hasattr(ob, 'on_remote_update'):
        ob.on_remote_update(args)
    else:
#      ob.logEvent('remote', 'created','') #testing
      if hasattr(ob, 'on_remote_new'):
#        open('/tmp/waa.txt','w').write(`ob.__dict__`)
        ob.on_remote_new(args)
  #      log('new')
  #  log('complete')
    return 'Updated %s %d' % (ob.__class__.__name__, ob.uid)
   
  @classmethod
  def remote_new(cls, uid):
    "Create a new database record and return it as a an object"
    sql = 'insert into %s(uid, id) values(%d, %s)' % (cls.table, int(uid), str(uid))
    execute(sql)
    return cls.get(uid)

  @classmethod
  def typecast(self, req):
    "make the request have the correct type as specified in _v_schema"
    for k in req:
      typ = self._v_schema.get(k,None)
      if typ:
        req[k]=typ(k)
    return req

def makeDataClass(Schema):
    "Set up a custom SQL data class"
    #dbc = Connection('makeDataClass')
    #db = Cursor(dbc)
    db = None
    # we only need to get the field info once per class 
    data = { #'db':db
       'table':Schema.tablesql
      , '_v_schema': Schema._v_schema
      , '_v_fields': Schema._v_schema.keys()
      }
    return type(Schema.table.capitalize(), (RemoteSQLDataObject,), data)
    

