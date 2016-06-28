# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
#from zope.component import getMultiAdapter
from plone import api
from DateTime import DateTime
#from plone.memoize import ram
#from time import time
from Products.CMFPlone.utils import safe_unicode


# 產製報表要寫到某個地方(ex. /tmp)，讓之後不用重複運算
class OrganizationView(BrowserView):
    """ Organization View
    """
    index = ViewPageTemplateFile("template/organization_view.pt")

    def get_this_year(self):
        return DateTime().year()

    def get_info_at_year(self, year):
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

        budget = 0
        cpcInfo = {}
        for item in brain:
            if item.budget:
                budget += item.budget
            if item.getObject().cpc:
                key = item.getObject().cpc.to_object.title
                if cpcInfo.get(key):
                    cpcInfo[key] += 1
                else:
                    cpcInfo[key] = 1
        return {'year':year, 'budget':budget, 'cpcInfo':cpcInfo}


    def __call__(self):
        context = self.context
        request = self.request
        portal = api.portal.get()

        return self.index()

