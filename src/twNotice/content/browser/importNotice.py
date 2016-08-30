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
from twNotice.content.browser.importRecent import BaseMethod


logger = logging.getLogger("IMPORT_NOTICE")


# 不刊公報 web.pcc.gov.tw/prkms/viewDailyTenderStatClient.do?dateString=20120622&searchMode=common&root=tps
# 刊登公報 web.pcc.gov.tw/prkms/prms-viewTenderStatClient.do?ds=20160414&root=tps

class ImportNotice(BrowserView, BaseMethod):
    """ Import Notice
    """

    def createContents(self, filename, container, ds):
        itemCount = 0
        for item in filename:
            try:
                with open('/tmp/%s' % item) as file:
                    notice = pickle.load(file)
                os.remove('/tmp/%s' % item)
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
            except:
                logger.error('line 58')
                continue
#            transaction.commit()
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
            noticeObject.noticeMeta = {}
            for key in notice.keys():
                noticeObject.noticeMeta[key] = notice[key]
#            logger.info('OK, Budget: %s, Title: %s' % (noticeObject.noticeMeta.get(u'預算金額'), noticeObject.title))
            itemCount += 1
            try:
                notify(ObjectModifiedEvent(noticeObject))
            except:
                logger.error('line 79')
                pass

            if itemCount % 5 == 0:
                transaction.commit()


    def importNotice(self, link, ds, searchMode):
        context = self.context
        request = self.request
        response = request.response
        catalog = context.portal_catalog
        portal = api.portal.get()
        intIds = component.getUtility(IIntIds)

        # 先確認folder
        container = self.getFolder(ds=ds, container=portal['notice'])
        # 取得公告首頁
        try:
            url = link # 條件未依需求修改
            htmlDoc = self.getList(url='%s&ds=%s' % (url, ds))
        except:
            logger.error('line 101')
            self.sendErrLog(3, url)
#            logger.error("網站無回應或被擋了 %s" % url)
            return

#        soup = BeautifulSoup(htmlDoc.read(), 'lxml')
        soup = BeautifulSoup(htmlDoc, 'lxml')

        filename = []
        itemCount = 0
        for item in soup.find_all('a', class_='tenderLink'):
            # 排除時間，暫用，之後移到configlet
            if DateTime().hour() in [3, 23]:
                break
            url = item['href']

            # 不刊登公報
            if searchMode:
                noticeURL = "http://web.pcc.gov.tw%s" % url
            # 刊登公報
            else:
                noticeURL = "http://web.pcc.gov.tw/prkms/prms-viewTenderDetailClient.do?ds=%s&fn=%s" % (ds, url)

            if 'twjavascript' in noticeURL:
                continue

            if catalog(noticeURL=noticeURL):
                continue

            id = '%s%s' % (DateTime().strftime('%Y%m%d%H%M%S'), random.randint(100000,999999))

            self.getPage(url=noticeURL, id=id)
            if os.path.exists('/tmp/%s' % id):
                logger.info('加1, %s' % noticeURL)
                filename.append(id)
            else:
                continue

            itemCount += 1
            if itemCount % 10 == 0:
                logger.info('Start Creat Contents: %s' % itemCount)
                if itemCount % 200 == 0:
                    api.portal.send_email(
                        recipient='andy@mingtak.com.tw',
                        sender='andy@mingtak.com.tw',
                        subject='%s Add notice: %s' % (ds, itemCount),
                        body='As title',
                    )
                self.createContents(filename, container, ds)
                transaction.commit()
                filename = []

        # 最後不足 200 要再做一次
        logger.info('Start Creat Contents: %s' % itemCount)
        self.createContents(filename, container, ds)
        logger.info('%s finish!' % ds)
        self.reportResult(ds, container)


    def __call__(self):
        context = self.context
        request = self.request
        response = request.response
        catalog = context.portal_catalog
        portal = api.portal.get()
#        intIds = component.getUtility(IIntIds)
        alsoProvides(request, IDisableCSRFProtection)

        logger.info('開始')
        if request.form.get('url'):
            # 配合 visudo
            self.reloadTor()
            link = request.form.get('url') # 條件未依需求修改
            ds = request.form.get('ds')
            searchMode = request.form.get('searchMode')
            self.importNotice(link, ds, searchMode)
        else:
            with open('/home/playgroup/noticeList') as file:
                logger.info('read file')
                for line in file:
                    # 排除時間，暫用，之後移到configlet
                    if DateTime().hour() in [3, 22, 22]:
                        return

                    # 配合 visudo
                    logger.info('This line is %s' % line)
                    try:
                        self.reloadTor()
                        link = line.split('&ds=')[0]
                        ds = line.split('&ds=')[1].strip()
                        searchMode = 'common' if 'searchMode' in line else None
                        self.importNotice(link, ds, searchMode)
                    except:
                        logger.error('line 191')
                        pass
