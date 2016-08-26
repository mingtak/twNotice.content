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
from plone import namedfile
import json
import os
import logging
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides
import transaction

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
        context = self.context
        portal = api.portal.get()

        sortedList = sorted(rawDict.items(), lambda x, y: cmp(x[1], y[1]))
        unPopList = self.clear_up_sortedList(sortedList, useBaseCount=False)

        if not context.report:
            context.report = {}

#        data = json.dumps(unPopList)
#        import pdb; pdb.set_trace()
        result = []
        for i in range(len(unPopList[0])):
            result.append({'label':unPopList[0][i], 'count':unPopList[1][i]})
        context.report['%s_raw' % resultString] = json.dumps(result)

        popList = self.clear_up_sortedList(sortedList)
        result = []
        for i in range(len(popList[0])):
            result.append({'label':popList[0][i], 'count':popList[1][i]})
        context.report['%s' % resultString] = json.dumps(result)

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
        if not exists_info:
            exists_info = [[], []]
        return [exists_info[0], exists_info[1]]


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

        tenderCount = 0 # 機關開標案數總計(cpc)
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
        if not exists_info:
            exists_info = [[], []]
        return [budget, tenderCount, exists_info[0], exists_info[1]]


    def __call__(self):
        context = self.context
        request = self.request
        portal = api.portal.get()

        return self.index()


class OrgReportView(OrganizationView):

    index = ViewPageTemplateFile("template/org_report_view.pt")


    def get_bar_data(self, dataString):
        context = self.context
        request = self.request
        data = context.report.get(dataString)
        data = data.replace('"count"', '"得標廠商"')

        if request.form.has_key('len'):
#            import pdb; pdb.set_trace()
            dataLen = len(json.loads(data))
            if dataLen:
                return dataLen
            else:
                return 1

        return data


    def get_pie_data(self, dataString):
        context = self.context
        request = self.request
        data = context.report.get(dataString)
        result = {}
        for item in json.loads(data):
            result[item['label']] = item['count']

        return json.dumps(result)


    def __call__(self):
        context = self.context
        request = self.request
        alsoProvides(request, IDisableCSRFProtection)

        data = request.form.get('data')

        if data and data.startswith('pie'):
            return self.get_pie_data(data.replace('pie', ''))

        if data and data.startswith('bar'):
            return self.get_bar_data(data.replace('bar', ''))


        if api.user.is_anonymous():
            self.canSee = False
        else:
            roles = api.user.get_roles()
            if list(set(roles) & set(['Reader', 'Site Administrator', 'Manager'])):
                self.canSee = True
            else:
                self.canSee = False
        return self.index()


class GetPieData(BrowserView):


    def __call__(self):
        context = self.context
        request = self.request
        alsoProvides(request, IDisableCSRFProtection)

        return json.loads(context.report['309380000Q_2015_winnerAmountInfo'])[1]


class ResetReport(BrowserView):

    def __call__(self):
        context = self.context
        request = self.request
        catalog = context.portal_catalog

        alsoProvides(request, IDisableCSRFProtection)

        brain = catalog(Type="Organization")
        count = 0
        for item in brain:
            item.getObject().report = None
            count += 1
            if count % 500 == 0:
                transaction.commit()
                logger.info('Reset Report, commit: %s' % count)

