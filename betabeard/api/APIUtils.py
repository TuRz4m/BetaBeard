'''
Created on 29 nov. 2013

@author: TuRz4m
'''
# -*- coding: utf-8 -*-

import json
import logging
import urllib
import urllib2
import urlparse
import hashlib

logger = logging.getLogger(__name__)

class APIBuilder:
    """
    Allow to build request from API.
    url : root of api.
    scheme : HTTP or https
    headers : HTTP Headers.
    params : Parameters for all message (like apikey). (In form of dictionnary).
    """
    def __init__(self,
                 urlRoot,
                 scheme="https",
                 headers=None,
                 params=None):
        self.urlRoot = urlRoot
        self.scheme = scheme
        self.headers = headers
        self.params = params
        # Init the container.
        if (self.params == None):
            self.params = []
        logger.debug("APIBuilder::__init__(urlRoot=%s,scheme=%s,headers=%s,params=%s)", urlRoot, scheme, headers, params)


    """
    Return all the param in form of string encoded. (param + param in obj).
    """
    def getParams(self, params=None):
        allParams = []
        logger.debug("APIBuilder::getParams(%s) [%s]", params, self.params)
        if (self.params != None):
            for p in self.params:
                allParams.append(p);
        if (params != None):
            for p in params:
                allParams.append(p);

        paramsEncoded = urllib.urlencode(allParams)
        logger.debug("APIBuilder::getParams(%s) => %s", params, paramsEncoded)
        return paramsEncoded

    """
    get the url for the api with the method & param.
    method : method called (like /members/infos)
    params : param to add to the request (like key=truc)
    """
    def getUrl(self, method, params=None):
        url = urlparse.urlunparse((self.scheme, self.urlRoot, method,
                                    None, self.getParams(params) , None))
        logger.debug("APIBuilder::getUrl(%s,%s) : %s", method, params, url)
        return url

    """
    Call a method on the API and get the response in form of python dictionnary.
    method : method called (like /members/infos)
    params : param to add to the request (in a dictionnary).
    post : if it's a post request.
    """
    def call(self, method, params=None, post=False):
        logger.debug("APIBuilder::call(%s,%s, %s)", method, params, post)
        opener = urllib2.build_opener()
        logger.debug("APIBuilder::call(%s,%s, %s) : Add Headers %s", method, params, post, self.headers)
        opener.addheaders = self.headers

        url = ""
        source = None
        try:
            # If Post : New header + data in content.
            if post:
                if (opener.addheaders != None):
                    opener.addheaders.append(('Content-Type', "application/x-www-form-urlencoded "))
                else:
                    opener.addheaders = [('Content-Type', "application/x-www-form-urlencoded ")]
                url = self.getUrl(method)
                source = opener.open(url, self.getParams(params))
            # if Get : we put the params in url.
            else:
                url = self.getUrl(method, params)
                source = opener.open(url)

            logger.debug("APIBuilder::call(%s) : Open connection (Post=%s)", url, post)
            json_data = json.loads(source.read())
            logger.debug("APIBuilder::call(%s,%s;%s) : %s", method, params, post, json_data)
            return json_data
        except urllib2.HTTPError as e:
            error = e.read()
            logger.error("APIBuilder::call(%s) : Error : %s (%s)", url, e.code, error)
            return json.loads(error)
        except urllib2.URLError as ex:
            logger.error("APIBuilder::call(%s) : Error : %s ", url, ex)
            return None








class BetaSerieAPI:
    def __init__(self,
                  login,
                  password,
                  key="cff7db294f72",
                  user_agent="BetaBeard"):
        headers = [('User-agent', user_agent),
                       ('X-BetaSeries-Version', '2.2'),
                       ('X-BetaSeries-Key', key)]
        self.builder = APIBuilder("api.betaseries.com", "https", headers)
        self.login = login;
        self.auth(login, password)
        self.builder.headers.append(('X-BetaSeries-Token', self.token))
        logger.debug("BetaSerieAPI::__init__(%s,%s)", key, login)


    """
    Auth a user and set the token.
    """
    def auth(self, login, password):
        hash_pass = hashlib.md5(password).hexdigest()
        logger.debug("BetaSerieAPI::auth(%s,%s) : Try auth...", login, hash_pass)
        params = [('login', login), ('password', hash_pass)]
        userAuth = self.builder.call("/members/auth", params, True)
        if (len(userAuth['errors']) == 0):
            self.idUser = userAuth['user']['id']
            self.token = userAuth['token']
            logger.debug("BetaSerieAPI::auth(%s,%s) : Successfull.", login, hash_pass)
        else:
            logger.error("BetaSerieAPI::auth(%s,%s) : Fail.", login, hash_pass)
            raise BadLoginException(userAuth['errors'][0])

    """
    Return the tvdbid of a show && title of this show.
    """
    def shows_tvdbid(self, show_id):
        params = [('id', show_id)]
        tvshow = self.builder.call("/shows/display" , params)
        if (len(tvshow['errors']) > 0):
            logger.debug("BetaSerieAPI::shows_tvdbid(%s) :  Show unknown (%s)", show_id, tvshow['errors'][0]['text'])
            return -1
        else:
            logger.debug("BetaSerieAPI::shows_tvdbid(%s) : %s", show_id, tvshow['show']['thetvdb_id'])
            return tvshow['show']['thetvdb_id'], tvshow['show']['title']


    """
    Add a show to the current user.
    """
    def add_show(self, show_id):
        params = [('id', show_id)]
        tvshow = self.builder.call("/shows/show" , params, True)
        if (len(tvshow['errors']) > 0):
            logger.debug("BetaSerieAPI::shows_tvdbid(%s) :  Error when adding the show. (%s)", show_id, tvshow['errors'][0]['text'])
            return False
        else:
            logger.debug("BetaSerieAPI::add_show(%s) : %s", show_id, tvshow)
            return True

    """
    Return the list of all the show (thetvdb_id) for the user.
    """
    def show_list(self):
        params = [('id', self.idUser)]
        memberinfo = self.builder.call("/members/infos", params)
        if (len(memberinfo['errors']) == 0):
            activeShows = []
            for show in memberinfo['member']['shows']:
                logger.debug("BetaSerieAPI::show_list() :  Show(%s) : %s", show['id'], show['title'])
                if show['status'] != 'Ended' and show['user']['archived'] == False:
                    activeShows.append(show['thetvdb_id'])
                    logger.debug("BetaSerieAPI::show_list() :  Show(%s) : %s Added.", show['id'], show['title'])
            return activeShows
        else:
            return []


    """
    Return the 100 first (or since) events on the timeline.
    """
    def timeline(self, nb=100, idUser=None, since=None):
        if (idUser == None):
            idUser = self.idUser

        params = [('id', idUser), ('nbpp', nb)]
        if (since != None):
            params.append(('since_id', since))

        timeline = self.builder.call("/timeline/member" , params)
        if (len(timeline['errors']) > 0):
            logger.debug("BetaSerieAPI::timeline(%s,%s,%s) :  Error when requesting timeling. (%s)", idUser, nb, since, timeline['show']['thetvdb_id'])
            return None
        else:
            logger.debug("BetaSerieAPI::timeline(%s,%s,%s) :  OK : %s", idUser, nb, since, timeline)
            return timeline['events']

    """
    Return all the events since the "since_id".
    We do it here, because the 'since_id' is funny...
    return last_id,events
    """
    def timeline_since(self, since=None, idUser=None):
        timeline = self.timeline(nb=100, idUser=idUser)

        if (timeline == None or len(timeline) == 0):
            return since, None

        last_id = timeline[0]['id'];
        events = []

        if (since == None):
            return last_id, []

        since = int(since)

        while timeline != None and len(timeline) != 0:
            for event in timeline:
                if (event['id'] <= since):
                    # we reverse because like this, it's in chronological order.
                    events.reverse()
                    return last_id, events;
                events.append(event);
            timeline = self.timeline(nb=100, since=events[len(events) - 1]['id'], idUser=idUser)


        events.reverse()
        return last_id, events.reverse()

    """
    Return all the events for show update (add/del/archive/unarchive).
    """
    def timeline_updateShow_since(self, since, idUser=None):
        last_id, events = self.timeline_since(since, idUser);
        maj = []
        for event in events:
            if (event['type'] == 'add_serie' or event['type'] == 'del_serie' or event['type'] == 'unarchive' or event['type'] == 'archive'):
                maj.append(event);
        return last_id, event;

    """
    Delete token in BetaSerie.
    """
    def __del__(self):
        self.builder.call("/members/destroy", None, True)


class BadLoginException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)



"""
SickBeard API.
We need to configure this one.
url: url of the sickbeard (like localhost:8081)
scheme : http/https
key: apikey of sickbeard
user_agent: User agent for request.
"""
class SickBeardAPI:
    def __init__(self,
                  url,
                  scheme="https",
                  key="cff7db294f72",
                  user_agent="BetaBeard"):
        headers = [('User-agent', user_agent)]
        self.builder = APIBuilder(url + "/api/" + key, scheme, headers)
        logger.debug("SickBeardAPI::__init__(%s,%s,%s,%s)", url, scheme, key, user_agent)

    """
    Just ping sickbeard.
    Return true if sickbeard answer.
    """
    def ping(self):
        params = [('cmd', 'sb.ping')]
        data = self.builder.call("/" , params)

        logger.debug("SickBeardAPI::ping() : %s",  data)

        if (data != None  and data['result'] == 'success'):
            return True
        elif (data != None):
            logger.error("SickBeard : Can't ping SickBeard. (%s)", data['message'])
        else:
            logger.error("SickBeard : Can't ping SickBeard.")

        return False

    """
    Add a show on sickbeard.
    tvdbid unique show id
    location path to existing folder to store show
    lang two letter tvdb language, en = english
    flatten_folders 0 - use season folders if part of rename string  1 - do not use season folders
    status wanted, skipped, archived, ignored
    initial multiple types can be passed when delimited by | : sdtv, sddvd, hdtv, rawhdtv, fullhdtv, hdwebdl, fullhdwebdl, hdbluray, fullhdbluray, unknown
    archive multiple types can be passed when delimited by | : sddvd, hdtv, rawhdtv, fullhdtv, hdwebdl, fullhdwebdl, hdbluray, fullhdbluray
    """
    def add_show(self, tvdbid, location=None, lang=None, flatten_folders=None, status=None, initial=None, archive=None):
        params = [('cmd', 'show.addnew'),
                   ('tvdbid', tvdbid)]
        if (location != None):
            params.append([('location', location)])
        if (lang != None):
            params.append([('lang', lang)])
        if (flatten_folders != None):
            params.append([('flatten_folders', flatten_folders)])
        if (status != None):
            params.append([('status', status)])
        if (initial != None):
            params.append([('initial', initial)])
        if (archive != None):
            params.append([('archive', archive)])
        data = self.builder.call("/" , params)
        logger.debug("SickBeardAPI::add_show(%s,%s,%s,%s,%s,%s,%s) : %s", tvdbid, location, lang, flatten_folders, status, initial, archive, data)

        if (data != None  and data['result'] == 'success'):
            return True
        elif (data != None):
            logger.error("SickBeard : Can't add show %s. (%s)", tvdbid, data['message'])
        else:
            logger.error("SickBeard : Can't add show %s.", tvdbid)

        return False

    """
    Delete the show on SickBeard.
    tvdbid = Id on thetvdb.
    """
    def del_show(self, tvdbid):
        params = [('cmd', 'show.delete'),
                   ('tvdbid', tvdbid)]
        data = self.builder.call("/" , params)
        logger.debug("SickBeardAPI::del_show(%s) : %s", tvdbid, data)

        if (data != None  and data['result'] == 'success'):
            return True
        elif (data != None):
            logger.error("SickBeard : Can't delete show %s. (%s)", tvdbid, data['message'])
        else:
            logger.error("SickBeard : Can't delete show %s.", tvdbid)

    """
    Pause the show on SickBeard.
    tvdbid = Id on thetvdb.
    pause = 0: Not paused, 1: paused.
    """
    def pause_show(self, tvdbid, pause):
        params = [('cmd', 'show.pause'),
                   ('tvdbid', tvdbid),
                   ('pause', pause)]
        data = self.builder.call("/" , params)
        logger.debug("SickBeardAPI::pause_show(%s, %s) : %s", tvdbid, pause, data)

        if (data != None  and data['result'] == 'success'):
            return True
        elif (data != None):
            logger.error("SickBeard : Can't pause/unpause show %s. (%s)", tvdbid, data['message'])
        else:
            logger.error("SickBeard : Can't pause/unpause show %s.", tvdbid)
        return False
