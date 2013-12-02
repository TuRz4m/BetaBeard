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
                opener.addheaders.append(('Content-Type', "application/x-www-form-urlencoded "))
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
            logger.error("APIBuilder::call(%s) : Error : %s (%s)", url, e.code, e.read())
            return None








class BetaSerieAPI:
    def __init__( self,
                  login,
                  password,
                  key="cff7db294f72",
                  user_agent="BetaBeard"):
        headers = [[('User-agent', user_agent)],
                       [('X-BetaSeries-Version', '2.2')],
                       [('X-BetaSeries-Key', key)]]
        self.builder = APIBuilder("api.betaseries.com", "http", headers)
        self.login = login;
        self.auth(login, password)
        self.builder.headers.append([('X-BetaSeries-Token', "xx")])
        logger.debug("BetaSerieAPI::__init__(%s,%s)", key, user_agent)


    """
    Auth a user and return the token.
    """
    def auth(self, login, password):
        hash_pass = hashlib.md5(password).hexdigest()
        params = urllib.urlencode({'login': login, 'password': hash_pass})
        # need to be in HTTPS during this request only.
        self.builder.scheme = "https"
        token = self.builder.call("/members/auth", params)
        print token

    """
    Return the tvdbid of a show.
    """
    def shows_tvdbid(self, show_id):
        params = urllib.urlencode({'id': show_id})
        tvshow = self.builder.call("/shows/display" , params)
        if (len(tvshow['errors']) > 0):
            return -1
        else:
            logger.debug("BetaSerieAPI::shows_tvdbid(%s) : %s", show_id, tvshow['show']['thetvdb_id'])
            return tvshow['show']['thetvdb_id']


    """
    Return the id of a member named 'login'
    """
    def members_id(self, login):
        params = urllib.urlencode({'login': login})
        member = self.builder.call("/members/search", params)
        if (len(member['users']) > 0):
            logger.debug("BetaSerieAPI::members_id(%s) : %s", login, member['users'][0]['id'])
            return member['users'][0]['id']
        else:
            logger.debug("BetaSerieAPI::members_id(%s) : User not found.", login)
            return -1
    """
    Return the list of all the show (thetvdb_id) for the user [user_id].
    """
    def show_list(self, user_id):
        params = urllib.urlencode({'id': user_id})
        memberinfo = self.builder.call("/members/infos", params)
        activeShows = []
        for show in memberinfo['member']['shows']:
            if show['status'] == 'continuing' & show['user']['archived'] == 'false':
                activeShows.append(show['thetvdb_id'])
        return activeShows


