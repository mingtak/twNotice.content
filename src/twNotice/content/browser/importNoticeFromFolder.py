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


logger = logging.getLogger("IMPORT_NOTICE")


# 不刊公報 web.pcc.gov.tw/prkms/viewDailyTenderStatClient.do?dateString=20120622&searchMode=common&root=tps
# 刊登公報 web.pcc.gov.tw/prkms/prms-viewTenderStatClient.do?ds=20160414&root=tps

class ImportNoticeFromFolder(BrowserView):
    """ Import Notice
    """
    def getFolder(self, ds):
        portal = api.portal.get()
        year = ds[0:4]
        month = ds[4:6]
        day = ds [6:8]

        notice = portal['notice']
        if not notice.get(year):
            api.content.create(type='Folder', title=year, container=notice)
            transaction.commit()
        if not notice[year].get(month):
            api.content.create(type='Folder', title=month, container=notice[year])
            transaction.commit()
        if not notice[year][month].get(day):
            api.content.create(type='Folder', title=day, container=notice[year][month])
            transaction.commit()
        return portal['notice'][year][month][day]


    def importNotice(self, doc, ds):
        context = self.context
        request = self.request
        response = request.response
        catalog = context.portal_catalog
        portal = api.portal.get()
        intIds = component.getUtility(IIntIds)

        # 先確認folder
        container = self.getFolder(ds=ds)

        if catalog(noticeURL=doc['noticeURL']):
            return

        id = '%s%s' % (DateTime().strftime('%Y%m%d%H%M%S'), random.randint(1000000,9999999))

        import pdb; pdb.set_trace()
        obj = api.content.create(
            type='Notice',
            container=container,
            id=notice['id'],
            title=doc[safe_unicode('標案名稱')],
            noticeType=notice.get('noticeType'),
            noticeURL=notice.get('noticeURL'),
            dateString=request.form.get('ds'),
            cpc=notice.get('cpc'),
        )

    def __call__(self):
        context = self.context
        request = self.request
        response = request.response
        catalog = context.portal_catalog
        portal = api.portal.get()
#        intIds = component.getUtility(IIntIds)

        filenames = os.popen('ls /home/playgroup/notice_to_disk').read().split()
        for filename in filenames:
            with open('/home/playgroup/notice_to_disk/%s' % filename) as file:
                try:

#                    import pdb; pdb.set_trace()
#                    os.system('sudo service tor reload')
#                    time.sleep(2)
                    doc = pickle.load(file)
                    if doc.get(safe_unicode('公告日')):
                        tmp = doc.get(safe_unicode('公告日'))
                        tmp = tmp.split('/')
                        ds = '%s%s%s' % (str(int(tmp[0])+1911), tmp[1], tmp[2])
                    elif doc.get(safe_unicode('決標公告日期')):
                        tmp = doc.get(safe_unicode('決標公告日期'))
                        tmp = tmp.split('/')
                        ds = '%s%s%s' % (str(int(tmp[0])+1911), tmp[1], tmp[2])
                    elif doc.get(safe_unicode('無法決標公告日期')):
                        tmp = doc.get(safe_unicode('無法決標公告日期'))
                        tmp = tmp.split('/')
                        ds = '%s%s%s' % (str(int(tmp[0])+1911), tmp[1], tmp[2])
                    else:
                        ds = '19700101'

                    self.importNotice(doc, ds)
                except:
                    pass
