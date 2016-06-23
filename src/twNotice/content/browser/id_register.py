# -*- coding: utf-8 -*-
from twNotice.content import _
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
#from zope.component import getMultiAdapter
from plone import api
from DateTime import DateTime
import urllib, urllib2
import json
import transaction


class IdLogin(BrowserView):
    """ Id Login """

    index = ViewPageTemplateFile("template/id_login.pt")

    def __call__(self):
        return self.index()


class JoinUs(BrowserView):
    """ Join Us """

    index = ViewPageTemplateFile("template/join_us.pt")

    def __call__(self):
        return self.index()

