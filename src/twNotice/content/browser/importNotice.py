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

#### proxy = urllib2.ProxyHandler({'http': aaa[15]})
# opener = urllib2.build_opener(proxy)
# opener.addheaders = URLLIB2_HEADER
# urllib2.install_opener(opener)

    def importNotice(self, link, ds, searchMode):
        context = self.context
        request = self.request
        response = request.response
        catalog = context.portal_catalog
        portal = api.portal.get()
        intIds = component.getUtility(IIntIds)

        testCount = int(request.form.get('testCount', 10))
        logger.info('testCount: %s' % testCount)
        while True:
            proxies = self.getProxies()
            if proxies:
                break

        # 先確認folder
        container = self.getFolder(ds=ds, container=portal['notice'])
        # 取得公告首頁
        try:
            url = link # 條件未依需求修改
            htmlDoc = self.getList(url='%s&ds=%s' % (url, ds), proxies=proxies)
        except:
            logger.error('line 101')
            self.sendErrLog(3, url)
#            logger.error("網站無回應或被擋了 %s" % url)
            return

#        soup = BeautifulSoup(htmlDoc.read(), 'lxml')
        soup = BeautifulSoup(htmlDoc, 'lxml')

        itemCount = 0
        logger.info('for loop 開始')
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

            if api.content.find(context=portal['notice'][ds[0:4]][ds[4:6]][ds[6:]], noticeURL=noticeURL):
                continue

            id = '%s%s' % (DateTime().strftime('%Y%m%d%H%M%S'), random.randint(100000,999999))

            if len(noticeURL) < 50:
                logger.info('值太短不處理 %s, %s' % (noticeURL, len(noticeURL)))
                continue # 網址太短表示有問題，不浪費時間
            if '&fn=PPW' in noticeURL or \
               '&fn=FAS' in noticeURL or \
               '&fn=DTG' in noticeURL or \
               '&fn=RML' in noticeURL or \
               '&fn=FAS' in noticeURL or \
               '&fn=FAR' in noticeURL:
                logger.info('非標案公告不處理 %s' % noticeURL)
                continue # 網址太短表示有問題，不浪費時間

            proxy = random.choice(proxies)

            noticeURL = noticeURL.replace('&', 'ZZZZZZZ') # 先把 & 替代掉，傳過去之後再換回來
            os.popen('curl "%s/@@get_page?id=%s&ds=%s&proxy=%s&folder=notice&noticeURL=%s"' % \
                (portal.absolute_url(), id, ds, proxy, noticeURL))
            logger.info('發出, %s' % noticeURL.replace('ZZZZZZZ', '&'))
            #TODO 休息多久，可以區分尖峰時間
#            time.sleep(30)

            itemCount += 1
            if itemCount == testCount:
                logger.info('先測 %s 筆' % itemCount)
                break
        logger.info('%s 完成!' % ds)
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

                    logger.info('This line is %s' % line)
                    try:
                        link = line.split('&ds=')[0]
                        ds = line.split('&ds=')[1].strip()
                        searchMode = 'common' if 'searchMode' in line else None
                        self.importNotice(link, ds, searchMode)
                    except:
                        logger.error('line 191')
                        pass
