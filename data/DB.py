"""
CJH ..we only ever want DictCursors these days,
  so here is a DictCursor dispatcher for the whole app
IHM : no default database now,
  we set the datbase explicitly with the table (April 2007)

"""
from MySQLdb import connect as MySQLconnect
from MySQLdb.cursors import DictCursor
from MySQLdb.connections import OperationalError
from pool import Pool, Constructor
from twisted.enterprise import adbapi
from twisted.internet.defer import inlineCallbacks, returnValue
from time import time, sleep
from base import Logging

logger = Logging.get_logger('DB')


class DB(object):
    "manage pooled database access"

    def __init__(self, connect_config=None):
        """set up connection pool if config is available.
       This allows the legacy pattern of app setup
       by calling init_db to continue.
    """
        if connect_config:
            self.init(connect_config)

    def init(self, connect_config):
        "set up connection pools"
        # allow for legacy config
        # - check for space and comma delimited strings
        if type(connect_config) == str:
            if ',' in connect_config:
                delim = ','
            else:
                delim = ' '
            connect_config = connect_config.split(delim)
            #print(
            #    'Deprecated: database connection should be a tuple not a string'
            #)

        host, user, pw = connect_config
        self.conn_pool = Pool(
            Constructor(self.connect, host, user, pw, charset='utf8'),
            poolsize=8)
        self.async_pool = adbapi.ConnectionPool(
            'MySQLdb', host, user, pw, charset='utf8', cursorclass=DictCursor)

    def execute(self, sql, args=None, dbc=None, transact=True):
        "perform a query safely"
        #start = time()
        dbc = dbc or self.conn_pool.get()
        db = dbc.cursor(DictCursor)
        #print '------', sql, args
        try:
            if transact:
                dbc.begin()
#      try:
#print '-----execute'
            db.execute(sql, args)
            #       except OperationalError:
            #         dbc = self.conn_pool.get()
            #         db = dbc.cursor(DictCursor)
            #         db.execute(sql, args)
            if 'INSERT' in sql.upper():
                # return the insert id
                insert_id = dbc.insert_id()
            if transact:
                dbc.commit()
            #print '------done'
        except:
            logger.debug(str((sql, args)), exc_info=True)
            dbc.rollback()
            raise

        if 'INSERT' in sql.upper():
            # return the insert id
            res = insert_id
        else:
            # return the result seT
            res = db.fetchall()
        db.close()
        # Disconnect(dbc)
        self.conn_pool.put(dbc)
        del db, dbc
        #print '--------complete'

        #end = time()
        #logger.debug("%.6f\t%s\t%s" % (end-start, sql, str(args)))

        return res

    @inlineCallbacks
    def aexecute(self, sql, *params):
        "execute query asyncrously"

        if 'INSERT' in sql.upper():
            # for INSERT we would like to return the insert id
            def insert(db):
                "insert a record, return its insert id"
                db.execute(sql, params)
                return db.connection.insert_id()

            uid = yield self.async_pool.runInteraction(insert)
            returnValue(uid)
        else:
            l = yield self.async_pool.runQuery(sql, *params)
            returnValue(l)

    def connect(self, *args, **kwargs):
        "connect to MySQL and intialise connection. Used by syncrous interface"
        dbc = MySQLconnect(*args, **kwargs)
        # override this method to give the required answer at all times!
        dbc.character_set_name = lambda: 'utf8'
        return dbc


# #### Legacy Support


def init_db(connect_config):
    "call this first!"
    db.init(connect_config)


# DB is a singleton object
# init_db should be called first, per established custom
db = DB()
execute = db.execute
aexecute = db.aexecute
