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


    def get_related(self):
        context = self.context
        catalog = context.portal_catalog

        pccOrgCode = context.noticeMeta.get(safe_unicode('機關代碼'))
        noticeId = context.noticeMeta.get(safe_unicode('標案案號'))
        noticeTraceCode = '%s--%s' % (pccOrgCode, noticeId)
        brain = catalog(noticeTraceCode=noticeTraceCode, sort_on='dateString')
        return brain


    def traceState(self):
        context = self.context
        request = self.request
        portal = api.portal.get()

        if api.user.is_anonymous():
            return 'anon'

        currentId = api.user.get_current().id
        noticeTraceCode = '%s--%s' % (context.noticeMeta.get(u'機關代碼'), context.noticeMeta.get(u'標案案號'))
        profile = portal['members'][currentId]

        if not profile.noticeTraceCode:
            return 'untrace'

        if noticeTraceCode in profile.noticeTraceCode:
            return 'trace'
        else:
            return 'untrace'


    def __call__(self):
        return self.index()

