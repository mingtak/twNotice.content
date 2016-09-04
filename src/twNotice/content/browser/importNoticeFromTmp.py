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
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides

logger = logging.getLogger("IMPORT_NOTICE_FORM_FOLDER")


# 不刊公報 web.pcc.gov.tw/prkms/viewDailyTenderStatClient.do?dateString=20120622&searchMode=common&root=tps
# 刊登公報 web.pcc.gov.tw/prkms/prms-viewTenderStatClient.do?ds=20160414&root=tps

class ImportNoticeFromTmp(BrowserView):
    """ Import Notice
    """

    def getFolder(self, ds, container):
        portal = api.portal.get()
        year = ds[0:4]
        month = ds[4:6]
        day = ds [6:8]

        if not container.get(year):
            api.content.create(type='Folder', title=year, container=container)
        if not container[year].get(month):
            api.content.create(type='Folder', title=month, container=container[year])
        if not container[year][month].get(day):
            api.content.create(type='Folder', title=day, container=container[year][month])
        return container[year][month][day]


    def __call__(self):
        context = self.context
        request = self.request
        response = request.response
        catalog = context.portal_catalog
        portal = api.portal.get()
        alsoProvides(request, IDisableCSRFProtection)

        files = os.popen('ls /tmp/twNotice*')

        logger.info('新增開始')
        for filename in files:
            filename = filename.strip()
            with open(filename) as file:
                notice = pickle.load(file)

            ds=notice['dateString']
            folder = notice['folder']
            container = portal[folder]
            container = self.getFolder(container=container, ds=ds)


            if api.content.find(context=container, noticeURL=notice.get('noticeURL')):
                logger.info('有了刪掉 %s' % noticeURL)
                os.remove(filename)
                continue

            noticeObject = api.content.create(
                type='Notice',
                container=container,
                id=notice['id'],
                title=notice['title'],
                noticeType=notice.get('noticeType'),
                noticeURL=notice.get('noticeURL'),
                dateString=ds,
                cpc=notice.get('cpc'),
            )
            api.content.transition(obj=noticeObject, transition='publish')

#            except:
#                logger.error('line 58')
#                continue
            if notice.has_key('id'):
                notice.pop('id')
            if notice.has_key('title'):
                notice.pop('title')
            if notice.has_key('noticeType'):
                notice.pop('noticeType')
            if notice.has_key('noticeURL'):
                notice.pop('noticeURL')
            if notice.has_key('cpc'):
                notice.pop('cpc')
            if notice.has_key('ds'):
                notice.pop('ds')
            if notice.has_key('folder'):
                notice.pop('folder')

            noticeObject.noticeMeta = {}
            for key in notice.keys():
                noticeObject.noticeMeta[key] = notice[key]
#            logger.info('OK, Budget: %s, Title: %s' % (noticeObject.noticeMeta.get(u'預算金額'), noticeObject.title))
            try:
                notify(ObjectModifiedEvent(noticeObject))
            except:
                logger.error('line 79')
                pass
            logger.info('新增完成 %s-%s' % (ds, filename))
            transaction.commit()
            os.remove(filename)
