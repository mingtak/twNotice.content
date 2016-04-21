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
import time
from Products.CMFPlone.utils import safe_unicode
from ..config import GET_HEADERS, NOTICE_SCOPE
from multiprocessing import Process
import re
import random


logger = logging.getLogger("IMPORT_NOTICE")


# 不刊公報 web.pcc.gov.tw/prkms/viewDailyTenderStatClient.do?dateString=20120622&searchMode=common&root=tps
# 刊登公報 web.pcc.gov.tw/prkms/prms-viewTenderStatClient.do?ds=20160414&root=tps

class ImportNotice(BrowserView):
    """ Import Notice
    """
    proxy = urllib2.ProxyHandler({'http': 'proxy.hinet.net'})
    opener = urllib2.build_opener(proxy)

    def getList(self,url):
        urllib2.install_opener(self.opener)
        urlRequest = urllib2.Request(url, headers=GET_HEADERS)
        return urllib2.urlopen(urlRequest)


    def getPage(self, url):
        portal = api.portal.get()

        urllib2.install_opener(self.opener)
        urlRequest = urllib2.Request(url, headers=GET_HEADERS)
        htmlDoc = urllib2.urlopen(urlRequest)

        noticeSoup = BeautifulSoup(htmlDoc, 'lxml')
        all_th = noticeSoup.find_all('th', class_='T11b')

        id = '%s%s' % (DateTime().strftime('%Y%m%d%H%M%S'), random.randint(10000,99999))
        title = noticeSoup.find('th', class_='T11b', text='標案名稱').find_next_sibling('td').get_text().strip()
        noticeType = noticeSoup.h1.get_text() if noticeSoup.h1 else noticeSoup.find('td', class_='T11c').get_text()
        try:
            cpc = re.findall('[0-9]+', noticeSoup.find('th', text='標的分類').find_next_sibling('td').get_text())[0]
        except:
            cpc = None

        intIds = component.getUtility(IIntIds)
        try:
            cpcObject = api.content.find(id=cpc)[0].getObject()
        except:
            cpcObject = None

        notice = api.content.create(
            type='Notice',
            id=id,
            title=title,
            noticeType=noticeType,
            noticeURL=url,
            container=portal['notice'],
        )

        if cpcObject:
            notice.cpc=RelationValue(intIds.getId(cpcObject))

        logger.info(id)
        notice.noticeMeta = {}
        for th in all_th:
            notice.noticeMeta[th.get_text()] = th.find_next_sibling('td').get_text().strip()

#        transaction.commit()


    def __call__(self):
        context = self.context
        request = self.request
        response = request.response
        catalog = context.portal_catalog
        portal = api.portal.get()
        intIds = component.getUtility(IIntIds)

        #取得公告首頁
        try:
            url = request.form.get('url') # 條件未依需求修改
# 刊登公報
# http://60.251.139.32:8510/twNotice/import_notice?url=http://web.pcc.gov.tw/prkms/prms-viewTenderStatClient.do?root=tps&ds=20100107
# 不刊登公報
# http://60.251.139.32:8510/twNotice/import_notice?url=http://web.pcc.gov.tw/prkms/viewDailyTenderStatClient.do?dateString=20160415&searchMode=common&root=tps&ds=20160415
            htmlDoc = self.getList(url='%s&ds=%s' % (url, request.form.get('ds')))
        except:
            logger.error("網站無回應或被擋了")
            raise IOError('web site NO Response')

        soup = BeautifulSoup(htmlDoc.read(), 'lxml')

        multi_process = []
        for item in soup.find_all('a', class_='tenderLink'):
            url = item['href']

            # 不刊登公報
            if request.form.get('searchMode'):
                noticeURL = "http://web.pcc.gov.tw%s" % url
            # 刊登公報
            else:
                noticeURL = "http://web.pcc.gov.tw/prkms/prms-viewTenderDetailClient.do?ds=%s&fn=%s" % (request.form.get('ds'), url)

#            self.getPage(url=noticeURL)
#            break
            multi_process.append(Process(target = self.getPage, kwargs={'url':noticeURL}))

        for process in multi_process:
            process.start()
            time.sleep(2)

        logger.info('完成')
        transaction.commit()
