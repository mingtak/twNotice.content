# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
#from zope.component import getMultiAdapter
from plone import api
import requesocks
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
import time
from Products.CMFPlone.utils import safe_unicode
from ..config import GET_HEADERS, NOTICE_SCOPE
import re
import os
import random
import pickle


logger = logging.getLogger("Fix CPC")


class FixCPC(BrowserView):
    """ Fix CPC
    """
    def __call__(self):
        context = self.context
        request = self.request
        response = request.response
        catalog = context.portal_catalog
        portal = api.portal.get()

        logger.info('開始')
        brain = catalog(Type='Notice')
        logger.info('Brain OK, %s' % len(brain[340000:]))
        count = 0
        for item in brain[340000:]:
            count +=1
            notice = item.getObject()
            if not notice.cpc:
                logger.info('沒有CPC: %s' % item.getURL())
                continue
            if notice.cpc.to_object.Type() != 'CPC':
                id = notice.cpc.to_object.id
                try:
                    cpcObject = api.content.find(Type='CPC', id=id)[0].getObject()
                except:
                    logger.info('沒有cpcObject: %s' % item.getURL())
                    cpcObject = None
                if cpcObject:
                    intIds = component.getUtility(IIntIds)
                    notice.cpc = RelationValue(intIds.getId(cpcObject))
                    notify(ObjectModifiedEvent(notice))
                    logger.info('fixed item: %s' % item.getURL())
            if count % 1000 == 0:
                logger.info('進度: %s' % count)
                transaction.commit()
        transaction.commit()
