# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
#from zope.component import getMultiAdapter
from plone import api
from DateTime import DateTime
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

    def get_this_year(self):
        return DateTime().year()


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

        # 因為json內容要改，所以這段要改
        if year != self.get_this_year() and os.path.exists('%s/%s_%s_winnerInfo' % (rPath, context.id, year)):
            with open('%s/%s_%s_winnerInfo' % (rPath, context.id, year)) as file:
                winnerInfo = json.load(file)
            return winnerInfo

        brain = api.content.find(context=portal['notice'][str(year)],
                                 Type='Notice',
                                 pccOrgCode=context.pccOrgCode,
                                 noticeType=[safe_unicode('決標公告'),
                                             safe_unicode('定期彙送'),]
                                )

        winnerInfo = {} # 投標廠商資訊, ex. {'XX公司':[n, m]} , n:得標件數, m:得標金額合計
        for item in brain:
            winner = item.winner
            if len(winner) == 1:
                key = winner[0]
                try:
                    money = int(filter(unicode.isdigit, item.getObject().noticeMeta.get(safe_unicode('決標金額'), '0')))
                except:
                    money = int(filter(str.isdigit, item.getObject().noticeMeta.get(safe_unicode('決標金額'), '0')))
                winnerInfo[key] = [winnerInfo.get(key, [0, 0])[0] + 1,
                                   winnerInfo.get(key, [0, 0])[1] + money]

        if year != self.get_this_year() and not os.path.exists('%s/%s_%s_winnerInfo' % (rPath, context.id, year)):
            unsorted = sorted(winnerInfo.items(), lambda x, y: cmp(x[1][1], y[1][1]), reverse=True)
            other = [0, 0]
            winnerInfo = {}
            for i in range(len(unsorted)):
                if i < 6:
                    winnerInfo[unsorted[i][0]] = unsorted[i][1]
                else:
                    other[0] += unsorted[i][1][0]
                    other[1] += unsorted[i][1][1]
                    winnerInfo['Other'] = other


            with open('%s/%s_%s_winnerInfo' % (rPath, context.id, year), 'w') as file:
#                import pdb; pdb.set_trace()
#                file.write(json.dumps(winnerInfo, encoding='unicode'))
                file.write(json.dumps(winnerInfo))
        return winnerInfo


    def get_tender_at_year(self, year):
        context = self.context
        request = self.request
        portal = api.portal.get()

        brain = api.content.find(context=portal['notice'][str(year)],
                                 Type='Notice',
                                 pccOrgCode=context.pccOrgCode,
                                 noticeType=[safe_unicode('公開招標公告'),
                                             safe_unicode('限制性招標(經公開評選或公開徵求)公告'),
                                             safe_unicode('選擇性招標(建立合格廠商名單)公告'),
                                             safe_unicode('選擇性招標(個案)公告'),
                                             safe_unicode('公開取得報價單或企劃書公告'),]
                                )

        budget = 0 # 機關預算總計
        cpcInfo = {} # CPC, ex. {'CPC分類':[n, m]} , n:開標分類件數, m:開標分類預算分計
        for item in brain:
            if item.budget:
                budget += item.budget
            if item.getObject().cpc:
                key = item.getObject().cpc.to_object.title
                if key.isdigit():
                    import pdb; pdb.set_trace()
                cpcInfo[key] = cpcInfo.get(key, [0, 0])
                cpcInfo[key][0] += 1
                if item.budget:
                    cpcInfo[key][1] += getattr(item, 'budget', 0)
#應建檔，檔名：year_orgCode , 例：2015_313201500G

        return {'budget':budget, 'cpcInfo':cpcInfo}


    def __call__(self):
        context = self.context
        request = self.request
        portal = api.portal.get()

        return self.index()


class OrgReportView(OrganizationView):

    index = ViewPageTemplateFile("template/org_report_view.pt")

    def __call__(self):
        return self.index()
