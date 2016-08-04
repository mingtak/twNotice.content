# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
#from zope.component import getMultiAdapter
from plone import api
import urllib2
import csv
from bs4 import BeautifulSoup
from z3c.relationfield.relation import RelationValue
from zope import component
from zope.app.intid.interfaces import IIntIds
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent, ObjectModifiedEvent
from DateTime import DateTime
import transaction
import logging
from Products.CMFPlone.utils import safe_unicode
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides


logger = logging.getLogger("twNotice.content.import_cpc")


class ImportCPC(BrowserView):
    """ Import CPC
    """
    def __call__(self):
        context = self.context
        request = self.request
        response = request.response
        catalog = context.portal_catalog
        portal = api.portal.get()
        intIds = component.getUtility(IIntIds)

        alsoProvides(request, IDisableCSRFProtection)

        with open('/home/playgroup/CpcOpenData.xml') as file:
            soup = BeautifulSoup(file.read(), 'xml')

        for item in soup.find_all(safe_unicode('採購標的')):
            cpc = api.content.create(
                type='CPC',
                id=safe_unicode(getattr(item, '標的代碼').string.encode('utf-8')),
                title=safe_unicode(getattr(item, '分類名稱中文').string.encode('utf-8')),
                engTitle=safe_unicode(getattr(item, '分類名稱英文').string.encode('utf-8')),
                noticeCategory=safe_unicode(getattr(item, '標的分類').string.encode('utf-8')),
                container=portal['resource']['category']
            )
            cpc.childrenCPC = {cpc.id:cpc.title}
            if getattr(item, '本分類之下1層CPC細項').string:
                for cpcsub in getattr(item, '本分類之下1層CPC細項').string.split(','):
                    key = cpcsub.split()[0]
                    value = cpcsub.split()[1]
                    cpc.childrenCPC[key] = value
            notify(ObjectModifiedEvent(cpc))
            logger.info(cpc.title)
