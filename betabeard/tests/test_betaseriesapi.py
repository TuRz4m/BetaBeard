'''
Created on 29 nov. 2013

@author: NEE
'''
# -*- coding: utf-8 -*-

from unittest import TestCase, TestSuite, TestLoader, TextTestRunner

from api.APIUtils import BetaSerieAPI


class BetaSerieAPITestCase(TestCase):

    def setUp(self):
        self.betaserieAPI = BetaSerieAPI("Dev047", "developer")
        self.assertEqual(self.betaserieAPI.builder.getUrl("", ""), "https://api.betaseries.com")
        self.assertIsNotNone(self.betaserieAPI.token)
        self.assertIsNotNone(self.betaserieAPI.idUser)

    def test_shows_tvdbid(self):
        idShow = 2410
        thetvdb_id = 0
        self.assertEqual(self.betaserieAPI.shows_tvdbid(idShow), thetvdb_id)


    def test_show_list(self):
        print self.betaserieAPI.show_list()


    def suite(self):
        suite = TestSuite()
        suite.addTest(TestLoader().loadTestsFromTestCase(BetaSerieAPITestCase))
        return suite


    if __name__ == '__main__':
        TextTestRunner().run(suite())