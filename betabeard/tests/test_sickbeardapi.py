'''
Created on 05 dec. 2013

@author: TuRz4m
'''
# -*- coding: utf-8 -*-

from unittest import TestCase, TestSuite, TestLoader, TextTestRunner

from api.APIUtils import SickBeardAPI
import time


class SickBeardAPITestCase(TestCase):
    idShow = 2410

    def setUp(self):
        self.sickBeardAPI = SickBeardAPI("localhost:8081", "https", "0f82b885553028ed594211e0b2a6de4f")
        self.assertEqual(self.sickBeardAPI.builder.getUrl("", ""), "https://localhost:8081/api/0f82b885553028ed594211e0b2a6de4f")

    def test_add_show(self):
        self.assertFalse(self.sickBeardAPI.add_show(0)[0])

    def test_del_show(self):
        self.assertFalse(self.sickBeardAPI.del_show(0)[0])

    def test_pause_show(self):
        self.assertFalse(self.sickBeardAPI.pause_show(0, 0)[0])
        self.assertFalse(self.sickBeardAPI.pause_show(0, 1)[0])
        self.assertFalse(self.sickBeardAPI.pause_show(0, 50)[0])

    def test_workflow(self):
        showId = 268906
        self.assertTrue(self.sickBeardAPI.add_show(showId)[0])
        # need to sleep, otherwise, the show is not added.
        time.sleep(5)
        self.assertTrue(self.sickBeardAPI.pause_show(showId, 1)[0])
        self.assertTrue(self.sickBeardAPI.pause_show(showId, 1)[0])
        self.assertTrue(self.sickBeardAPI.pause_show(showId, 0)[0])
        self.assertTrue(self.sickBeardAPI.pause_show(showId, 0)[0])

        self.assertFalse(self.sickBeardAPI.del_show(showId)[0])
        self.assertEqual(self.sickBeardAPI.del_show(showId)[1], "Show can not be deleted while being added or updated")
        time.sleep(10)
        self.assertTrue(self.sickBeardAPI.del_show(showId)[0])
        self.assertFalse(self.sickBeardAPI.pause_show(showId, 1)[0])


    def suite(self):
        suite = TestSuite()
        suite.addTest(TestLoader().loadTestsFromTestCase(SickBeardAPITestCase))
        return suite


    if __name__ == '__main__':
        TextTestRunner().run(suite())