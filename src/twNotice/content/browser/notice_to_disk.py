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

class NoticeToDisk(BrowserView):
    """ Import Notice
    """
    session = requesocks.session()
    #Use Tor for both HTTP and HTTPS
    session.proxies = {'http': 'socks5://localhost:9050', 'https': 'socks5://localhost:9050'}

    def sessionGet(self, url):
        errCount = 0
        while True:
            try:
                responDoc = self.session.get(url, timeout=5)
                break
            except:
                if errCount >= 5:
                    logger.info('洋蔥失敗5次, %s' % url)
#                    import pdb; pdb.set_trace()
                    return ''
                else:
                   errCount +=1
                os.system('sudo service tor reload')
                time.sleep(random.randint(2,8))
#                logger.info('洋蔥重啟_%s, %s' % (errCount, url))
                continue
        return responDoc.text

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

        with open('/home/playgroup/notice_to_disk/%s' % id, 'w') as file:
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

        filename = []
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
            id = '%s%s' % (DateTime().strftime('%Y%m%d%H%M%S'), random.randint(100000,999999))
            filename.append(id)
            self.getPage(url=noticeURL, id=id)

        logger.info('%s, 完成, finish!' % ds)


    def __call__(self):
        context = self.context
        request = self.request
        response = request.response
        catalog = context.portal_catalog
        portal = api.portal.get()
#        intIds = component.getUtility(IIntIds)

        tempFileName = request.form.get('fname')
        with open('/home/playgroup/notice_menu/%s' % tempFileName) as file:
            for line in file:
                # 配合 visudo
                try:
#                    os.system('sudo service tor reload')
#                    time.sleep(2)
                    link = line.split('&ds=')[0]
                    ds = line.split('&ds=')[1].strip()
                    searchMode = 'common' if 'searchMode' in line else None
                    self.importNotice(link, ds, searchMode)
                except:pass
