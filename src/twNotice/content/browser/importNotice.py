# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
#from zope.component import getMultiAdapter
from plone import api
import requesocks
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
import os
import random
import pickle


logger = logging.getLogger("IMPORT_NOTICE")


# 不刊公報 web.pcc.gov.tw/prkms/viewDailyTenderStatClient.do?dateString=20120622&searchMode=common&root=tps
# 刊登公報 web.pcc.gov.tw/prkms/prms-viewTenderStatClient.do?ds=20160414&root=tps

class ImportNotice(BrowserView):
    """ Import Notice
    """
    proxy = urllib2.ProxyHandler({'http': 'proxy.hinet.net'})
    opener = urllib2.build_opener(proxy)
    session = requesocks.session()
    #Use Tor for both HTTP and HTTPS
    session.proxies = {'http': 'socks5://localhost:9050', 'https': 'socks5://localhost:9050'}

    def reportResult(self, ds):
        year = ds[0:4]
        month = ds[4:6]
        day = ds [6:8]
        portal = api.portal.get()
        count = len(portal['notice'][year][month][day].getChildNodes())

        api.portal.send_email(recipient='andy@mingtak.com.tw',
            sender='andy@mingtak.com.tw',
            subject="完成回報",
            body="日期：%s, Count: %s" % (ds, count),
        )


    def sendErrLog(self, position, url):
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


    def getList(self,url):
        urllib2.install_opener(self.opener)
        urlRequest = urllib2.Request(url, headers=GET_HEADERS)
#        return urllib2.urlopen(urlRequest)
        return self.session.get(url).text


    def getPage(self, url, id):
        portal = api.portal.get()

        urllib2.install_opener(self.opener)
        urlRequest = urllib2.Request(url, headers=GET_HEADERS)
        try:
#            htmlDoc = urllib2.urlopen(urlRequest)
            htmlDoc = self.session.get(url).text
        except:
            self.sendErrLog(1, url)
            logger.error('urlopen Error, %s' % url)
            return

        noticeSoup = BeautifulSoup(htmlDoc, 'lxml')
        all_th = noticeSoup.find_all('th', class_='T11b')
        try:
            title = noticeSoup.find('th', class_='T11b', text='標案名稱').find_next_sibling('td').get_text().strip()
            noticeType = noticeSoup.h1.get_text() if noticeSoup.h1 else noticeSoup.find('td', class_='T11c').get_text()
        except:
            self.sendErrLog(2, url)
            logger.error('at getPage, %s' % url)
            return
        try:
            cpc = re.findall('[0-9]+', noticeSoup.find('th', text='標的分類').find_next_sibling('td').get_text())[0]
        except:
            cpc = None

        intIds = component.getUtility(IIntIds)
        try:
            cpcObject = api.content.find(id=cpc)[0].getObject()
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

        logger.info(id)
        for th in all_th:
            if notice.has_key(th.get_text().strip()):
                keyIndex = 1
                logger.info(th.get_text().strip())
                while True:
                    newKey = u'%s_%s' % (th.get_text().strip(), keyIndex)
                    logger.info('newkey: %s, %s' % (newKey, notice.has_key(newKey)))
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


    def importNotice(self, link, ds, searchMode):
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
            url = link # 條件未依需求修改
            htmlDoc = self.getList(url='%s&ds=%s' % (url, ds))
        except:
            self.sendErrLog(3, url)
            logger.error("網站無回應或被擋了 %s" % url)
            return

#        soup = BeautifulSoup(htmlDoc.read(), 'lxml')
        soup = BeautifulSoup(htmlDoc, 'lxml')

        multi_process, filename = [], []
        for item in soup.find_all('a', class_='tenderLink'):
            url = item['href']

            # 不刊登公報
            if searchMode:
                noticeURL = "http://web.pcc.gov.tw%s" % url
            # 刊登公報
            else:
                noticeURL = "http://web.pcc.gov.tw/prkms/prms-viewTenderDetailClient.do?ds=%s&fn=%s" % (ds, url)

            if catalog(noticeURL=noticeURL):
                continue
            id = '%s%s' % (DateTime().strftime('%Y%m%d%H%M%S'), random.randint(10000,99999))
            filename.append(id)
            multi_process.append(Process(target = self.getPage, kwargs={'url':noticeURL, 'id':id}))

        for process in multi_process:
            process.start()
            time.sleep(2)

        # 正式前時間設長一點 200！
        time.sleep(20)
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
                    dateString=request.form.get('ds'),
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
            logger.info('OK, Budget: %s, Title: %s' % (noticeObject.noticeMeta.get(u'預算金額'), noticeObject.title))
            itemCount += 1
            try:
                notify(ObjectModifiedEvent(noticeObject))
            except:pass
        transaction.commit() 
        logger.info('%s finish!' % ds)
        self.reportResult(ds)


    def __call__(self):
        context = self.context
        request = self.request
        response = request.response
        catalog = context.portal_catalog
        portal = api.portal.get()
#        intIds = component.getUtility(IIntIds)

        if request.form.get('url'):
            # 配合 visudo
            os.system('sudo service tor reload')
            link = request.form.get('url') # 條件未依需求修改
            ds = request.form.get('ds')
            searchMode = request.form.get('searchMode')
            self.importNotice(link, ds, searchMode)
        else:
            with open('/home/playgroup/noticeList') as file:
                for line in file:
                    # 配合 visudo
                    try:
                        os.system('sudo service tor reload')
                        time.sleep(5)
                        link = line.split('&ds=')[0]
                        ds = line.split('&ds=')[1].strip()
                        searchMode = 'common' if 'searchMode' in line else None
                        self.importNotice(link, ds, searchMode)
                    except:pass
