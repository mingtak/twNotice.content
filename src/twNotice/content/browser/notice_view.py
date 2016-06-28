# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
#from zope.component import getMultiAdapter
from plone import api
from DateTime import DateTime
#from plone.memoize import ram
#from time import time
from Products.CMFPlone.utils import safe_unicode


class NoticeView(BrowserView):
    """ Notice View
    """
    index = ViewPageTemplateFile("template/notice_view.pt")

    def get_org(self):
        context = self.context
        portal = api.portal.get()

        code = self.context.noticeMeta.get(safe_unicode('機關代碼'))
        if not code:
            return
        org = api.content.find(context=portal['resource']['organization'],
                               Type='Organization',
                               pccOrgCode=code)
        if not org:
            return

        if len(org) == 1:
            # return a Organization's brain item
            return org[0]
        else:
            return


    def get_deadline(self):
        context = self.context
        deadline = context.noticeMeta.get(safe_unicode('截止投標'))
        return deadline


    def __call__(self):
        return self.index()

