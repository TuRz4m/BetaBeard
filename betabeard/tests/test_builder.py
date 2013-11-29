'''
Created on 29 nov. 2013

@author: NEE
'''
# -*- coding: utf-8 -*-

from unittest import TestCase, TestSuite, TestLoader, TextTestRunner

import BetaBeard


class BuilderTestCase(TestCase):

    def setUp(self):
        url = "api.betaseries.com"
        scheme = "http"
        headers = [[('User-agent', "BetaBeard")], [('X-BetaSeries-Version', '2.2')]]
        params = "key=cff7db294f72";
        self.builder = BetaBeard.APIBuilder(url, scheme, headers, params)

        self.assertEqual(self.builder.urlRoot, url)
        self.assertEqual(self.builder.scheme, scheme)
        self.assertEqual(self.builder.headers, headers)
        self.assertEqual(self.builder.params, params)

    def test_url(self):
        method = "/members/search"
        params= "login=TuRz4m"
        url = self.builder.getUrl(method, params)
        self.assertEqual(url, "http://api.betaseries.com/members/search?key=cff7db294f72&login=TuRz4m")

    def test_response(self):
        method = "/members/search"
        params= "login=TuRz4m"
        url = self.builder.getUrl(method, params)
        self.assertIsNotNone(self.builder.getResponse(url))

    def test_call(self):
        method = "/members/search"
        params= "login=TuRz4m"
        self.assertEquals(self.builder.call(method, params)['users'][0]['login'], "TuRz4m")

    def suite(self):
        suite = TestSuite()
        suite.addTest(TestLoader().loadTestsFromTestCase(BuilderTestCase))
        return suite


    if __name__ == '__main__':
        TextTestRunner().run(suite())