#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ads` package."""

import unittest
import os
import shutil
from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse
from delivery import *

import sys
sys.path.append('../')

class TestAds(unittest.TestCase):
    # Test validateInputsForCreate against valid input for create API
    def test_create_validateInputsForCreate_withTrue(self):
        #data_feed = dataFeed()
        create = Create()
        args={
            "Source":"Delhi",
            "Destination":"Pune"
        }

        p=create.validateInputsForCreate(args)
        self.assertTrue(p)
        args=None

    # Test validateInputsForCreate against invalid input for create API
    def test_create_validateInputsForCreate_withFalse(self):
        #data_feed = dataFeed()
        create = Create()
        args=None

        args={
            "Source":"Delhi"
        }

        p=create.validateInputsForCreate(args)
        self.assertFalse(p)

    def test_getFilePath(self):
        self.assertEquals(getFilePath("testFile"),  './adsstorage/testFile.txt')

    def test_getFilePath_withFalse(self):
        self.assertFalse(isFileExists("FileDontExists"))

    def test_getFilePath_withTrue(self):
        if not os.path.exists('adsstorage'):
            os.makedirs('adsstorage')
        open("adsstorage/fileExists.txt", "a+")
        self.assertTrue(isFileExists("fileExists"))

        self.addCleanup(shutil.rmtree, 'adsstorage')

    def test_create(self):
        app = Flask(__name__)
        api = Api(app)
        setupParser()
        setupBasicConfigs()
        addResources(api)
        m = Create()

        with app.test_request_context('/create', data={'Source': 'Pune', 'Destination':'Mumbai'}):
            p=m.post()
            self.assertEquals(p[1],  200)
        self.addCleanup(shutil.rmtree, 'adsstorage')
        self.addCleanup(shutil.rmtree, 'ads-logs')

    def test_Update(self):
        app = Flask(__name__)
        api = Api(app)
        setupParser()
        setupBasicConfigs()
        addResources(api)
        create = Create()
        update = Update()

        id=""
        with app.test_request_context('/create', data={'Source': 'Pune', 'Destination':'Mumbai'}):
            p=create.post()
            id=p[0].split(" ")[-1]

            self.assertEquals(p[1],  200)

        with app.test_request_context('/update', data={'Id': id, 'Date': 'new-date', 'Location': 'new-location'}):
            p=update.put()
            self.assertEquals(p[0],  "Package updated ")
            self.assertEquals(p[1],  200)

        self.addCleanup(shutil.rmtree, 'adsstorage')
        self.addCleanup(shutil.rmtree, 'ads-logs')

    def test_CheckProgress(self):
        app = Flask(__name__)
        api = Api(app)
        setupParser()
        setupBasicConfigs()
        addResources(api)
        create = Create()
        checkProgress = CheckProgress()
        update = Update()

        id=""
        with app.test_request_context('/create', data={'Source': 'Pune', 'Destination':'Mumbai'}):
            p=create.post()
            id=p[0].split(" ")[-1]

            self.assertEquals(p[1],  200)

        with app.test_request_context('/update', data={'Id': id, 'Date': 'new-date', 'Location': 'new-location'}):
            p=update.put()
            self.assertEquals(p[0],  "Package updated ")
            self.assertEquals(p[1],  200)

        with app.test_request_context('/check_progress', data={'Id': id}):
            p=checkProgress.get()
            self.assertEquals(p[1]['Date'],  'new-date')
            self.assertEquals(p[1]['Location'],  'new-location')

        self.addCleanup(shutil.rmtree, 'adsstorage')
        self.addCleanup(shutil.rmtree, 'ads-logs')

    def test_MarkDelivery(self):
        app = Flask(__name__)
        api = Api(app)
        setupParser()
        setupBasicConfigs()
        addResources(api)
        create = Create()
        markD = MarkDelivery()

        id=""
        with app.test_request_context('/create', data={'Source': 'Pune', 'Destination':'Mumbai'}):
            p=create.post()
            id=p[0].split(" ")[-1]

            self.assertEquals(p[1],  200)

        with app.test_request_context('/mark_delivery', data={'Id': id}):
            p=markD.put()
            self.assertEquals(p[0],  "package is marked as Delivered: ")
            self.assertEquals(p[1],  200)


        self.addCleanup(shutil.rmtree, 'adsstorage')
        self.addCleanup(shutil.rmtree, 'ads-logs')

if __name__ == '__main__':
    unittest.main()
