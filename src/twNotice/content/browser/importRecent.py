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


logger = logging.getLogger("IMPORT_RECENT")
TODAY_URL = 'http://web.pcc.gov.tw/pishtml/todaytender.html'


class ImportRecent(BrowserView):
    """ Import Recent
    """
    session = requesocks.session()
    #Use Tor for both HTTP and HTTPS
    session.proxies = {'http': 'socks5://localhost:9050', 'https': 'socks5://localhost:9050'}

    def sessionGet(self, url):
        errCount = 0
        while True:
            try:
                responDoc = self.session.get(url, timeout=3)
                break
            except:
                if errCount >= 5:
                    logger.info('洋蔥失敗5次, %s' % url)
#                    import pdb; pdb.set_trace()
                    return ''
                else:
                   errCount +=1
                logger.info('洋蔥失敗%s次, %s' % (errCount, url))
                os.system('sudo service tor reload')
                time.sleep(2)
#                logger.info('洋蔥重啟_%s, %s' % (errCount, url))
                continue
        return responDoc.text

    def reportResult(self, ds):
        year = ds[0:4]
        month = ds[4:6]
        day = ds [6:8]
        portal = api.portal.get()
        count = len(portal['recent'][year][month][day].getChildNodes())

        api.portal.send_email(recipient='andy@mingtak.com.tw',
            sender='andy@mingtak.com.tw',
            subject="完成回報",
            body="日期：%s, Count: %s" % (ds, count),
        )


    def sendErrLog(self, position, url):
        return # 先不寄
        api.portal.send_email(recipient='andy@mingtak.com.tw',
            sender='andy@mingtak.com.tw',
            subject="URL OPEN錯誤回報",
            body="位置%s, 被擋了, %s" % (position, url),
        )


    def getFolder(self, ds):
        portal = api.portal.get()
        year = ds[0:4]
        month = ds[4:6]
        day = ds [6:8]

        recent = portal['recent']
        if not recent.get(year):
            api.content.create(type='Folder', title=year, container=recent)
#            transaction.commit()
        if not recent[year].get(month):
            api.content.create(type='Folder', title=month, container=recent[year])
#            transaction.commit()
        if not recent[year][month].get(day):
            api.content.create(type='Folder', title=day, container=recent[year][month])
#            transaction.commit()
        return portal['recent'][year][month][day]


    def getList(self,url):
        return self.sessionGet(url)


    def getPage(self, url, id):
        portal = api.portal.get()

        htmlDoc = self.sessionGet(url)
        noticeSoup = BeautifulSoup(htmlDoc, 'lxml')
        all_th = noticeSoup.find_all('th', class_='T11b')
        try:
            title = noticeSoup.find('th', class_='T11b', text='標案名稱').find_next_sibling('td').get_text().strip()
            noticeType = noticeSoup.h1.get_text() if noticeSoup.h1 else noticeSoup.find('td', class_='T11c').get_text()
        except:
            self.sendErrLog(2, url)
#            logger.error('at getPage, %s' % url)
            return
        try:
            cpc = re.findall('[0-9]+', noticeSoup.find('th', text='標的分類').find_next_sibling('td').get_text())[0]
        except:
            cpc = None

        intIds = component.getUtility(IIntIds)
        try:
            cpcObject = api.content.find(Type='CPC', id=cpc)[0].getObject()
        except:
            cpcObject = None

        notice = {
            'id':id,
            'title':title,
            'noticeType':noticeType,
            'noticeURL':url,
        }

        if cpcObject:
            notice['cpc'] = RelationValue(intIds.getId(cpcObject))

#        logger.info(id)
        for th in all_th:
            if notice.has_key(th.get_text().strip()):
                keyIndex = 1
#                logger.info(th.get_text().strip())
                while True:
                    newKey = u'%s_%s' % (th.get_text().strip(), keyIndex)
#                    logger.info('newkey: %s, %s' % (newKey, notice.has_key(newKey)))
                    if notice.has_key(newKey):
                        keyIndex += 1
                    else:
                        notice[newKey] = th.find_next_sibling('td').get_text().strip()
                        break
            else:
                notice[th.get_text().strip()] = th.find_next_sibling('td').get_text().strip()

        with open('/tmp/%s' % id, 'w') as file:
            pickle.dump(notice, file)
        return


    def importNotice(self, link, ds):
        context = self.context
        request = self.request
        response = request.response
        catalog = context.portal_catalog
        portal = api.portal.get()
        intIds = component.getUtility(IIntIds)

        # 先確認folder
        container = self.getFolder(ds=ds)
        # 取得公告首頁
        try:
            url = link
            htmlDoc = self.getList(url=url)
        except:
            self.sendErrLog(3, url)
#            logger.error("網站無回應或被擋了 %s" % url)
            return

#        soup = BeautifulSoup(htmlDoc.read(), 'lxml')
        soup = BeautifulSoup(htmlDoc, 'lxml')

        filename = []
        itemCount = 0

        for item in soup.find_all('a'):
            if 'detail' not in item.get('href', ''):
                continue
            url = item.get('href')

            noticeURL = "http://web.pcc.gov.tw%s" % url

            if catalog(noticeURL=noticeURL):
                continue
            id = '%s%s' % (DateTime().strftime('%Y%m%d%H%M%S'), random.randint(100000,999999))
            filename.append(id)
            self.getPage(url=noticeURL, id=id)

            itemCount += 1
            if itemCount % 200 == 0:
                api.portal.send_email(
                    recipient='andy@mingtak.com.tw',
                    sender='andy@mingtak.com.tw',
                    subject='%s Add notice: %s' % (ds, itemCount),
                    body='As title',
                )
                transaction.commit()
        logger.info('完成')

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
            except:
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
            except:pass
#        transaction.commit()
        logger.info('%s finish!' % ds)
        self.reportResult(ds)


    def __call__(self):
        context = self.context
        request = self.request
        response = request.response
        catalog = context.portal_catalog
        portal = api.portal.get()
#        intIds = component.getUtility(IIntIds)
        alsoProvides(request, IDisableCSRFProtection)

        logger.info('開始')
        # 配合 visudo
        os.system('sudo service tor reload')
        time.sleep(2)
        link = TODAY_URL
        ds = DateTime().strftime('%Y%m%d')
        self.importNotice(link, ds)
