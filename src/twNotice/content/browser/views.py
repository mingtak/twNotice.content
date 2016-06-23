# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
#from zope.component import getMultiAdapter
from plone import api
from DateTime import DateTime
import transaction
from plone.memoize import ram
from time import time

from Acquisition import aq_inner
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.security import checkPermission
from zc.relation.interfaces import ICatalog


def back_references(source_object, attribute_name):

    catalog = getUtility(ICatalog)
    intids = getUtility(IIntIds)
    result = []
    for rel in catalog.findRelations(
                dict(to_id=intids.getId(aq_inner(source_object)),
                from_attribute=attribute_name)):
        obj = intids.queryObject(rel.from_id)
        if obj is not None and checkPermission('zope2.View', obj):
            result.append(obj)
            # 太龐大，只找100筆
            if len(result) > 100:
                break
    return result


class ProfileView(BrowserView):
    """ Profile View
    """
    index = ViewPageTemplateFile("template/profile_view.pt")

    def __call__(self):
        return self.index()


class OrganizationView(BrowserView):
    """ Organization View
    """
    index = ViewPageTemplateFile("template/organization_view.pt")

    def __call__(self):
        return self.index()


class CPCView(BrowserView):
    """ CPC View
    """
    index = ViewPageTemplateFile("template/cpc_view.pt")

    def __call__(self):
        context = self.context
        self.back_ref = back_references(context, 'cpc')
        return self.index()


class NoticeView(BrowserView):
    """ Notice View
    """
    index = ViewPageTemplateFile("template/notice_view.pt")

    def __call__(self):
        return self.index()


class CoverView(BrowserView):
    """ Cover View
    """
    index = ViewPageTemplateFile("template/cover_view.pt")

# 開站後 ram cache要加回去 60*60*3 意指每3小時更新一次結果
#    @ram.cache(lambda *args: time() // (60 * 60 * 3))
    def getBrain(self, cpc):
        context = self.context
        catalog = context.portal_catalog
        brain = {}
        for cpc in context.cpc:
            brain[cpc] = catalog({'cpc':cpc}, sort_on='created', sort_order='reverse')[0:10]
        return brain


    def __call__(self):
        context = self.context
        self.brain = self.getBrain(context.cpc)
        return self.index()


class WithoutPT(BrowserView):
    """ Without PT View
    """
