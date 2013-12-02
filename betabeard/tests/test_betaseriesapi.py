'''
Created on 29 nov. 2013

@author: NEE
'''
# -*- coding: utf-8 -*-

from unittest import TestCase, TestSuite, TestLoader, TextTestRunner

from api.APIUtils import BetaSerieAPI


class BetaSerieAPITestCase(TestCase):
    idShow = 2410
    # need to test on my user because there is no timeline on devUser.
    idUserTuRz4m = 15930

    def setUp(self):
        self.betaserieAPI = BetaSerieAPI("Dev047", "developer")
        self.assertEqual(self.betaserieAPI.builder.getUrl("", ""), "https://api.betaseries.com")
        self.assertIsNotNone(self.betaserieAPI.token)
        self.assertIsNotNone(self.betaserieAPI.idUser)
        self.betaserieAPI.add_show(self.idShow)

    def test_shows_tvdbid(self):
        thetvdb_id = 0
        self.assertEqual(self.betaserieAPI.shows_tvdbid(self.idShow), thetvdb_id)


    def test_show_list(self):
        self.assertIsNotNone(self.betaserieAPI.show_list())

    def test_timeline(self):
        self.assertIsNotNone(self.betaserieAPI.timeline(idUser=self.idUserTuRz4m))
        self.assertEqual(len(self.betaserieAPI.timeline(nb=4, idUser=self.idUserTuRz4m)), 4)

    def test_timelinesince(self):
        since = 70039042
        last_id, timeline = self.betaserieAPI.timeline_since(since=since, idUser=self.idUserTuRz4m);
        self.assertIsNotNone(timeline)
        self.assertGreater(len(timeline), 100)
        self.assertGreater(last_id, since)

    def test_timeline_updateShow_since(self):
        since = 70039042
        last_id, timeline = self.betaserieAPI.timeline_since(since=since, idUser=self.idUserTuRz4m);
        self.assertIsNotNone(timeline)
        self.assertGreater(len(timeline), 4)
        self.assertGreater(last_id, since)

    def suite(self):
        suite = TestSuite()
        suite.addTest(TestLoader().loadTestsFromTestCase(BetaSerieAPITestCase))
        return suite


    if __name__ == '__main__':
        TextTestRunner().run(suite())