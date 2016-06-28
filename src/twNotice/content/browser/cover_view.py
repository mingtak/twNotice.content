# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
#from zope.component import getMultiAdapter
from plone import api
from DateTime import DateTime
from plone.memoize import ram
from time import time


class CoverView(BrowserView):
    """ Cover View
    """
    index = ViewPageTemplateFile("template/cover_view.pt")

# 開站後 ram cache要加回去 60*60*3 意指每3小時更新一次結果
#    @ram.cache(lambda *args: time() // (60 * 60 * 3))
    def getBrain(self, cpc):
        context = self.context
        catalog = context.portal_catalog
        portal = api.portal.get()
        brain = {}
        for cpc in context.cpc:
            brain[cpc] = api.content.find(
                context=portal['recent'],
                cpc=cpc,
                sort_on='created',
                sort_order='reverse'
            )[0:5]
        return brain


    def __call__(self):
        context = self.context
        self.brain = self.getBrain(context.cpc)
        return self.index()
