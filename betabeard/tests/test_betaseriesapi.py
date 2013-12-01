'''
Created on 29 nov. 2013

@author: NEE
'''
# -*- coding: utf-8 -*-

from unittest import TestCase, TestSuite, TestLoader, TextTestRunner

from api.APIUtils import BetaSerieAPI


class BetaSerieAPITestCase(TestCase):

    def setUp(self):
        self.betaserieAPI = BetaSerieAPI("Dev47", "developer")
        self.assertEqual(self.betaserieAPI.builder.getUrl("", ""), "http://api.betaseries.com")

    def test_shows_tvdbid(self):
        idShow = 2410
        thetvdb_id = 0
        self.assertEqual(self.betaserieAPI.shows_tvdbid(idShow), thetvdb_id)

    def test_members_id(self):
        login = 'TuRz4m'
        user_id = 15930
        self.assertEqual(self.betaserieAPI.members_id(login), user_id)

        login = "fghfgdhfgjh"
        user_id = -1
        self.assertEqual(self.betaserieAPI.members_id(login), user_id)

    def test_show_list(self):
        user_id = 15930
        print self.betaserieAPI.show_list(user_id)


    def suite(self):
        suite = TestSuite()
        suite.addTest(TestLoader().loadTestsFromTestCase(BetaSerieAPITestCase))
        return suite


    if __name__ == '__main__':
        TextTestRunner().run(suite())