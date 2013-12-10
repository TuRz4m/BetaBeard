'''
Created on 29 nov. 2013

@author: TuRz4m
'''
# -*- coding: utf-8 -*-

from unittest import TestCase, TestSuite, TestLoader, TextTestRunner

from api.APIUtils import APIBuilder
import logging
logging.getLogger(__name__).addHandler(logging.StreamHandler())
logging.getLogger(__name__).setLevel(logging.DEBUG)

class BuilderTestCase(TestCase):

    def setUp(self):
        url = "api.betaseries.com"
        scheme = "https"
        headers = [('User-agent', "BetaBeard"), ('X-BetaSeries-Version', '2.2'), ('X-BetaSeries-Key', "cff7db294f72")]
        self.builder = APIBuilder(url, scheme, headers)

        self.assertEqual(self.builder.urlRoot, url)
        self.assertEqual(self.builder.scheme, scheme)
        self.assertEqual(self.builder.headers, headers)

    def test_url(self):
        method = "/members/search"
        paramBuilder = [('test', 'test2')]
        params= [('login', "TuRz4m")]
        url = self.builder.getUrl(method, params)
        self.assertEqual(url, "https://api.betaseries.com/members/search?login=TuRz4m")

        url = self.builder.getUrl(method)
        self.assertEqual(url, "https://api.betaseries.com/members/search")

        self.builder.params = paramBuilder;
        url = self.builder.getUrl(method, params)
        self.assertEqual(url, "https://api.betaseries.com/members/search?test=test2&login=TuRz4m")

        url = self.builder.getUrl(method)
        self.assertEqual(url, "https://api.betaseries.com/members/search?test=test2")



    def test_call(self):
        method = "/members/search"
        params= [('login', "TuRz4m")]
        self.assertEquals(self.builder.call(method, params)['users'][0]['login'], "TuRz4m")

    def test_post(self):
        method = "/members/auth"
        params= [('login', "Dev047"), ('password', '5e8edd851d2fdfbd7415232c67367cc3')]
        auth = self.builder.call(method, params, True);
        self.assertEquals(auth['user']['login'], "Dev047")

    def suite(self):
        suite = TestSuite()
        suite.addTest(TestLoader().loadTestsFromTestCase(BuilderTestCase))
        return suite


    if __name__ == '__main__':
        TextTestRunner().run(suite())