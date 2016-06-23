# -*- coding: utf-8 -*-
from twNotice.content import _
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
#from zope.component import getMultiAdapter
from plone import api
import urllib, urllib2
import json
import transaction


class Subscribe(BrowserView):

    template = ViewPageTemplateFile("template/subscribe.pt")


    def post(self, url, data):
        req = urllib2.Request(url)
        data = urllib.urlencode(data)
        #enable cookie
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        response = opener.open(req, data)
        return response.read()


    def __call__(self):
        context = self.context

