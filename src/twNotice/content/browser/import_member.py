# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from plone import api
from DateTime import DateTime
import time
from Products.CMFPlone.utils import safe_unicode
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides
import csv
import logging


logger = logging.getLogger("ImportMember")

class ImportMember(BrowserView):
    """ Import Member
    """

    def __call__(self):
        context = self.context
        request = self.request
        catalog = context.portal_catalog
        portal = api.portal.get()
        alsoProvides(request, IDisableCSRFProtection)

        with open("/home/playgroup/member.csv", "rb") as file:
            members = csv.DictReader(file)
            for item in members:
                if not item.get('id'):
                    continue
                if self.confirmProfile(item.get('id')):
                    continue
                profile = api.content.create(
                    type='Profile',
                    container=portal['members'],
                    id='fb%s' % item.get('id'),
                    title=item.get('name'),
                    email=item.get('email'),
                )
                # 還缺一個 subscribe attribute value
                profile.traceKeywords = []
                for keyword in item.get('keywords').split():
                    profile.traceKeywords.append(keyword)


    def confirmProfile(self, id):
        return api.content.find(Type='Profile', id='fb%s' % id)
