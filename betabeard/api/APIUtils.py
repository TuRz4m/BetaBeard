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
    params : Parameters for all message (like apikey).
    """
    def __init__(self,
                 urlRoot,
                 scheme="http",
                 headers=None,
                 params=None):
        self.urlRoot = urlRoot
        self.scheme = scheme
        self.headers = headers
        self.params = params
        logger.debug("APIBuilder::__init__(urlRoot=%s,scheme=%s,headers=%s,params=%s)", urlRoot, scheme, headers, params)



    """
    get the url for the api with the method & param.
    method : method called (like /members/infos)
    params : param to add to the request (like key=truc)
    """
    def getUrl(self, method, params=None):
        query = ""
        if (params != None):
            if (self.params != None):
                query = '%s&%s' % (self.params, params)
            else:
                query = params
        else:
            query = self.params

        url = urlparse.urlunparse((self.scheme, self.urlRoot, method,
                                    None, query, None))
        logger.debug("APIBuilder::getUrl(%s,%s) : %s", method, params, url)
        return url

    """
    Call an url an retrieve the answer.
    url : Url to call.
    """
    def getResponse(self, url):
        opener = urllib2.build_opener()
        for header in self.headers:
            logger.debug("APIBuilder::getResponse(%s) : %s", url, header)
            opener.addheaders = header
        source = opener.open(url)
        logger.debug("APIBuilder::getResponse(%s) : Open connection", url)
        return source.read()

    """
    Call a method on the API and get the response in form of python dictionnary.
    method : method called (like /members/infos)
    params : param to add to the request (like key=truc)
    """
    def call(self, method, param=None):
        logger.debug("APIBuilder::call(%s,%s)", method, param)
        source = self.getResponse(self.getUrl(method, param))
        json_data = json.loads(source)
        logger.debug("APIBuilder::call(%s,%s) : %s", method, param, json_data)
        return json_data

    """
    Call a method in POST.
    """
    def post(self, method, param=None):
        try:
            url = urlparse.urlunparse((self.scheme, self.urlRoot, method,
                                        None, None, None))
            req = urllib2.Request(url, param);
            response = urllib2.urlopen(req)
            json_data = json.loads(response)
            return json_data
        except  urllib2.HTTPError as error:
            logger.error("Error HTTP : %s", error.reason)




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
        self.builder.scheme = "http"
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


