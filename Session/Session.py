""" Browser session - used for login etc
"""
from datetime import datetime, timedelta

class Session(object):
  ""
  @classmethod
  def fetch_user(self, req):
    "get or create session object by id, validate and return the related user"

    guest = self.User.get(1) # fetch_user('guest')

    # the user will either be identified by a pre-identified req.request.avatarId
    # or the req will include __user__ and __pw__
    # FOR NOW: avatarId takes precedence;
    nocred = False
    avatarId = getattr(req.request, 'avatarId', None) #req.request.avatarId
    if avatarId and avatarId != 'guest':
      user = self.User.fetch_user(avatarId) or guest  # fetch_user returns none if user not recognised
      print "we have an avatar: ", avatarId, " maps to user ", user.id 
    elif '__user__' in req and '__pass__' in req:
      user = self.User.fetch_if_valid(req['__user__'], req['__pass__']) or guest # returns guest if not valid
      print "we have a login, __user__ ", req['__user__'], " maps to user ", user.id
    else:
      user = guest
      nocred = True
      print "no credentials - we assume guest unless the session tells us otherwise"

    id = req.request.getSession().uid

    # look for an existing session
    sessions = self.list(id=id, stage='')
    if sessions:
      print "Found a session", id
      session = sessions[0]
      # check the request against the content of the session
      criteria = [
          session.ip == req.request.getClientIP()
        , session.forwarded == self.get_forwarded(req)  
          ]
      # if any of our checks fail expire the session
      if not all(criteria):
        req.request.getSession().expire()
        print "ip address didn't match."
        return guest

      # user identity:  if the session user is guest but another user has
      # been identified in the request we detect a login and update the
      # session's user.  If the user doesn't match we expire the
      # session and return guest (uid=1)
      
      # session.user is guest and req.user is guest:  return guest
      if session.user == guest.uid and user.uid == guest.uid:
        print "definitely a guest"
        return guest

      # session has a user and no credentials have been offered
      # return the user specified in the session
      if session.user != guest.uid and nocred:
        print "no credentials provided but the session has a valid user"
        return self.User.get(session.user)  

      # session user != guest and req.user differs: expire session, return guest
      if session.user != guest.uid and session.user != user.uid:
        print "user doesn't match the session"
        req.request.getSession().expire()
        return guest

      # session.user is guest and req.user != guest: update.session user and return user
      if session.user == guest.uid and user.uid != guest.uid:
        print "user matches the session"
        session.user = user.uid
        session.flush()
        return user

    else:
      print "creating new session", id
      session = self.new()
      session.id = id
      session.user = user.uid
      session.ip = req.request.getClientIP()
      session.forwarded = self.get_forwarded(req)
      session.expires = datetime.now() + timedelta(days=1)
      session.flush()

    return user

  @classmethod
  def get_forwarded(self, req):
    "return the X-Forwarded-For header from the request as a string"
    return str(dict(req.request.requestHeaders.getAllRawHeaders()).get('X-Forwarded-For', ''))
    
