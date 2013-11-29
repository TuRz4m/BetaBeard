'''
Created on 29 nov. 2013

@author: NEE
'''
# -*- coding: utf-8 -*-

import urlparse
import urllib2
import json
import logging
import urllib
from distutils.tests.setuptools_build_ext import if_dl

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
        query = '%s&%s' % (self.params, params)
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
        logger.debug("APIBuilder::call(%s,%s) : %s", json_data['root'])
        return json_data['root']


class BetaSerieAPI:
    def __init__( self,
                  key="cff7db294f72",
                  user_agent="BetaBeard"):
        headers = [[('User-agent', user_agent)],
                       [('X-BetaSeries-Version', '2.2')],
                       [('X-BetaSeries-Key', key)]]
        self.builder = APIBuilder("api.betaseries.com", "http", headers)


    """
    Return the tvdbid of a show.
    """
    def shows_tvdbid(self, show_id):
        params = urllib.urlencode({'id': show_id})
        tvshow = self.build.call("/shows/display/" , params)
        return tvshow['thetvdb_id']


    """
    Return the id of a member named 'login'
    """
    def members_id(self, login):
        params = urllib.urlencode({'login': login})
        member = self.build.call("/members/search", params)
        return member['id']

    """
    Return the list of all the show (thetvdb_id) for the user [user_id].
    """
    def show_list(self, user_id):
        params = urllib.urlencode({'id': user_id})
        memberinfo = self.build.call("/members/infos", params)
        activeShows = []
        for show in memberinfo['member']['shows']:
            if show['status'] == 'continuing' & show['user']['archived'] == 'false':
                activeShows.append(show['thetvdb_id'])
        return activeShows


