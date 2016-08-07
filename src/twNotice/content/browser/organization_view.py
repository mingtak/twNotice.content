# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
#from zope.component import getMultiAdapter
from plone import api
from DateTime import DateTime
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
#from plone.memoize import ram
#from time import time
from Products.CMFPlone.utils import safe_unicode
import json
import os
import logging

logger = logging.getLogger("Organization View")


# 產製報表要寫到某個地方(ex. /tmp)，讓之後不用重複運算
class OrganizationView(BrowserView):
    """ Organization View
    """
    index = ViewPageTemplateFile("template/organization_view.pt")

    def filter_punt(self, filter_str):
        punct = set(u''':!),.:;?]}¢'"、。〉》」』】〕〗〞︰︱︳﹐､﹒
                        ﹔﹕﹖﹗﹚﹜﹞！），．：；？｜｝︴︶︸︺︼︾﹀﹂﹄﹏､～￠
                        々‖•·ˇˉ―--′’”([{£¥'"‵〈《「『【〔〖（［｛￡￥〝︵︷︹︻
                        ︽︿﹁﹃﹙﹛﹝（｛“‘-—_…''')
        filterpunt = lambda s: ' '.join(filter(lambda x: x not in punct, s))
        return filterpunt(filter_str)


    def get_CPC(self, key):
        context = self.context
        request = self.request
        response = request.response
        catalog = context.portal_catalog

        keyword = self.filter_punt(safe_unicode(key))
        brain = catalog(Type='CPC', Title=keyword)
        if not brain:
            response.redirect(context.absolute_url())
        for item in brain:
            if self.filter_punt(safe_unicode(key)) == self.filter_punt(safe_unicode(item.Title)):
                return item

    def get_this_year(self):
        return DateTime().year()


    def get_pie(self, sortedList, filename, width=10, height=6):
        labels = sortedList[0]
        sizes = sortedList[1]
        font = font_manager.FontProperties(fname='/usr/share/fonts/truetype/wqy/wqy-microhei.ttc')
        plt.figure(figsize=(width, height))
        figText = plt.pie(sizes, labels=labels, shadow=True, startangle=90, autopct='%1.1f%%', radius=0.9)[1]
        for item in figText:
           item.set_fontproperties(font)
        plt.axis('equal')
        plt.savefig(filename)
        plt.close()
        return


    def clear_up_sortedList(self, sortedList, baseCount=7, useBaseCount=True):
        other = 0

        if len(sortedList) > baseCount and useBaseCount:
            i = len(sortedList)-1
            while i+1:
                if i <= (len(sortedList)-baseCount):
                    other += sortedList[i][1]
                    sortedList.pop(i)
                i -= 1

#        sortedList.reverse()
#        sortedList.append(('Other', other))
#        sortedList.reverse()
        result = [[], []]
        for item in sortedList:
            result[0].append(item[0])
            result[1].append(item[1])
        return result


    def get_exists_file(self, rPath, countString, amountString):
        if os.path.exists('%s/%s.raw' % (rPath, countString)) and os.path.exists('%s/%s.raw' % (rPath, amountString)):
            with open('%s/%s.raw' % (rPath, countString)) as file:
                countInfo = json.load(file)
            with open('%s/%s.raw' % (rPath, amountString)) as file:
                amountInfo = json.load(file)
            return [countInfo, amountInfo]
        else:
            return None


    def sort_info(self, rawDict, resultString, rPath):
        sortedList = sorted(rawDict.items(), lambda x, y: cmp(x[1], y[1]))

        unPopList = self.clear_up_sortedList(sortedList, useBaseCount=False)
        with open('%s/%s.raw' % (rPath, resultString), 'w') as file:
            file.write(json.dumps(unPopList))

        popList = self.clear_up_sortedList(sortedList)
        with open('%s/%s' % (rPath, resultString), 'w') as file:
            file.write(json.dumps(popList))

        self.get_pie(popList, '%s/%s.png' % (rPath, resultString))
        return


    def get_recent(self):
        context = self.context
        request = self.request
        portal = api.portal.get()

        brain = api.content.find(context=portal['recent'],
                                 Type='Notice',
                                 pccOrgCode=context.pccOrgCode,
                                 noticeType=[safe_unicode('公開招標公告'),
                                             safe_unicode('限制性招標(經公開評選或公開徵求)公告'),
                                             safe_unicode('選擇性招標(建立合格廠商名單)公告'),
                                             safe_unicode('選擇性招標(個案)公告'),
                                             safe_unicode('公開取得報價單或企劃書公告'),]
                                )
        return brain


    def get_winner_at_year(self, year):
        context = self.context
        request = self.request
        portal = api.portal.get()
        rPath = api.portal.get_registry_record('twNotice.content.browser.siteSetting.ISiteSetting.rReportPath')

        # 存在就讀檔，那今年的檔案要設固定的清除機制
        countString = '%s_%s_winnerCountInfo' % (context.id, year)
        amountString = '%s_%s_winnerAmountInfo' % (context.id, year)

        exists_info = self.get_exists_file(rPath, countString, amountString)
        if exists_info:
            return exists_info

        brain = api.content.find(context=portal['notice'][str(year)],
                                 Type='Notice',
                                 pccOrgCode=context.pccOrgCode,
                                 noticeType=[safe_unicode('決標公告'),
                                             safe_unicode('定期彙送'),]
                                )

        winnerCountInfo = {} # 投標廠商資訊, ex. {'XX公司':n} , n:得標件數
        winnerAmountInfo = {} # 投標廠商資訊, ex. {'XX公司':n} , n:得標金額合計
        for item in brain:
            winner = item.winner
            if len(winner) == 1:
                key = winner[0]
                try:
                    money = int(filter(unicode.isdigit, item.getObject().noticeMeta.get(safe_unicode('決標金額'), '0')))
                except:
                    money = int(filter(str.isdigit, item.getObject().noticeMeta.get(safe_unicode('決標金額'), '0')))
                winnerCountInfo[key] = winnerCountInfo.get(key, 0) + 1
                winnerAmountInfo[key] = winnerAmountInfo.get(key, 0) + money
        self.sort_info(winnerCountInfo, countString, rPath)
        self.sort_info(winnerAmountInfo, amountString, rPath)

        exists_info = self.get_exists_file(rPath, countString, amountString)
        return [exists_info[0], exists_info[1]]

#        return [winnerCountInfo, winnerAmountInfo]


    def get_tender_at_year(self, year):
        context = self.context
        request = self.request
        portal = api.portal.get()
        rPath = api.portal.get_registry_record('twNotice.content.browser.siteSetting.ISiteSetting.rReportPath')

        # 存在就讀檔，那今年的檔案要設固定的清除機制
        countString = '%s_%s_tenderCountInfo' % (context.id, year)
        amountString = '%s_%s_tenderAmountInfo' % (context.id, year)

        exists_info = self.get_exists_file(rPath, countString, amountString)
        if exists_info:
            tenderCount = 0
            budget = 0
            for item in exists_info[0][1]:
                tenderCount += item
            for item in exists_info[1][1]:
                budget += item

            return [budget, tenderCount, exists_info[0], exists_info[1]]

        brain = api.content.find(context=portal['notice'][str(year)],
                                 Type='Notice',
                                 pccOrgCode=context.pccOrgCode,
                                 noticeType=[safe_unicode('公開招標公告'),
                                             safe_unicode('限制性招標(經公開評選或公開徵求)公告'),
                                             safe_unicode('選擇性招標(建立合格廠商名單)公告'),
                                             safe_unicode('選擇性招標(個案)公告'),
                                             safe_unicode('公開取得報價單或企劃書公告'),]
                                )

        tenderCount = 0 # 機關開標案數總計
        budget = 0 # 機關預算總計
        cpcCountInfo = {} # CPC資訊, ex. {'cpc':n} , n:開標件數
        cpcAmountInfo = {} # CPC資訊, ex. {'cpc':n} , n:開標預算分計
        for item in brain:
            tenderCount += 1
            if item.budget:
                budget += item.budget
            if item.getObject().cpc:
                key = item.getObject().cpc.to_object.title
                cpcCountInfo[key] = cpcCountInfo.get(key, 0) + 1
                if item.budget:
                    cpcAmountInfo[key] = cpcAmountInfo.get(key, 0) + getattr(item, 'budget', 0)
        self.sort_info(cpcCountInfo, countString, rPath)
        self.sort_info(cpcAmountInfo, amountString, rPath)


        exists_info = self.get_exists_file(rPath, countString, amountString)
        return [budget, tenderCount, exists_info[0], exists_info[1]]

#        import pdb; pdb.set_trace()
#        return [budget, tenderCount, cpcCountInfo, cpcAmountInfo]


    def __call__(self):
        context = self.context
        request = self.request
        portal = api.portal.get()

        return self.index()


class OrgReportView(OrganizationView):

    index = ViewPageTemplateFile("template/org_report_view.pt")

    def __call__(self):
        return self.index()
