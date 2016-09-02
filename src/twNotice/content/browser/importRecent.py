# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
#from zope.component import getMultiAdapter
from plone import api
import requests
from requests import ConnectionError, ConnectTimeout
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
from ..config import GET_HEADERS
import re
import os
import random
import pickle
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides


logger = logging.getLogger("IMPORT_RECENT")
TODAY_URL = 'http://web.pcc.gov.tw/pishtml/todaytender.html'


class BaseMethod():
    """ BaseMethod
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


    def reloadTor(self):
        os.system('sudo service tor reload')
        return


    def sessionGet(self, url):
        session = requests.session()
        session.proxies = {'http': 'socks5://localhost:9050', 'https': 'socks5://localhost:9050'}

        errCount = 0
        while True:
            try:
                responDoc = session.get(url, headers=GET_HEADERS, timeout=(3, 5))
                if not responDoc:
                    #logger.error('值錯誤: 空值, %s' % url)
                    raise ValueError()
#                time.sleep(1)
                return responDoc.text
            except ConnectionError:
                logger.info('注意！ConnectionError, %s' % url)
                self.reloadTor()
                continue
            except ConnectTimeout:
                logger.error('第 46 行')
                self.reloadTor()
                continue
            except:
                self.reloadTor()
                logger.info('其他錯誤, %s' % url)
                return ''


    def reportResult(self, ds, container):
        year = ds[0:4]
        month = ds[4:6]
        day = ds [6:8]
        portal = api.portal.get()
        count = len(container.getChildNodes())

        api.portal.send_email(recipient='andy@mingtak.com.tw',
            sender='andy@mingtak.com.tw',
            subject="完成回報",
            body="日期：%s, Count: %s" % (ds, count),
        )
        transaction.commit()


    def sendErrLog(self, position, url):
        return # 先不寄
        api.portal.send_email(recipient='andy@mingtak.com.tw',
            sender='andy@mingtak.com.tw',
            subject="URL OPEN錯誤回報",
            body="位置%s, 被擋了, %s" % (position, url),
        )
        transaction.commit()


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


    def getList(self,url):
        return self.sessionGet(url)


    def getPage(self, url, id):
        portal = api.portal.get()

        htmlDoc = self.sessionGet(url)
        if not htmlDoc:
            logger.error('第 109 行, %s' % url)
            return

        noticeSoup = BeautifulSoup(htmlDoc, 'lxml')
        all_th = noticeSoup.find_all('th', class_='T11b')
        try:
            title = noticeSoup.find('th', class_='T11b', text='標案名稱').find_next_sibling('td').get_text().strip()
            noticeType = noticeSoup.h1.get_text() if noticeSoup.h1 else noticeSoup.find('td', class_='T11c').get_text()
        except:
            logger.error('第 117 行, %s' % url)
            self.sendErrLog(2, url)
            return
        try:
            cpc = re.findall('[0-9]+', noticeSoup.find('th', text='標的分類').find_next_sibling('td').get_text())[0]
        except:
            logger.error('第 124 行, %s' % url)
            cpc = None

        intIds = component.getUtility(IIntIds)
        try:
            cpcObject = api.content.find(Type='CPC', id=cpc)[0].getObject()
        except:
            logger.error('第 131 行, %s' % url)
            cpcObject = None

        notice = {
            'id':id,
            'title':title,
            'noticeType':noticeType,
            'noticeURL':url,
        }

        if cpcObject:
            notice['cpc'] = RelationValue(intIds.getId(cpcObject))

        for th in all_th:
            if notice.has_key(th.get_text().strip()):
                keyIndex = 1
                while True:
                    newKey = u'%s_%s' % (th.get_text().strip(), keyIndex)
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


class ImportRecent(BrowserView, BaseMethod):
    """ Import Recent
    """

    def importNotice(self, link, ds):
        context = self.context
        request = self.request
        response = request.response
        catalog = context.portal_catalog
        portal = api.portal.get()
        intIds = component.getUtility(IIntIds)

        # 先確認folder
        container = self.getFolder(ds=ds, container=portal['recent'])
        # 取得公告首頁
        try:
            url = link
            htmlDoc = self.getList(url=url)
        except:
            logger.error('第 184 行')
            self.sendErrLog(3, url)
#            logger.error("網站無回應或被擋了 %s" % url)
            return

        soup = BeautifulSoup(htmlDoc, 'lxml')

        filename = []
        itemCount = 0

        for item in soup.find_all('a'):
            if 'detail' not in item.get('href', ''):
                continue
            url = item.get('href')

            noticeURL = "http://web.pcc.gov.tw%s" % url

            logger.info('==> %s' % noticeURL)

            if api.content.find(context=portal['recent'][ds[0:4]][ds[4:6]][ds[6:]], noticeURL=noticeURL):
                logger.info('有了 %s' % noticeURL)
                continue
            id = '%s%s' % (DateTime().strftime('%Y%m%d%H%M%S'), random.randint(100000,999999))

            self.getPage(url=noticeURL, id=id)
            if os.path.exists('/tmp/%s' % id):
                filename.append(id)
            else:
                continue

            itemCount += 1
            logger.info('加 %s, %s' % (itemCount % 10, noticeURL))
            if itemCount % 2 == 0:
                logger.info('Start Create Contents: %s' % itemCount)
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

        logger.info('完成')
        self.createContents(filename, container, ds)
        logger.info('%s finish!' % ds)
        self.reportResult(ds, container)


    def __call__(self):
        context = self.context
        request = self.request
        response = request.response
        catalog = context.portal_catalog
        portal = api.portal.get()
        alsoProvides(request, IDisableCSRFProtection)

        logger.info('開始')
        link = TODAY_URL
        ds = DateTime().strftime('%Y%m%d')
        self.importNotice(link, ds)
