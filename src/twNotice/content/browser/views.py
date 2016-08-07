# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
#from zope.component import getMultiAdapter
from plone import api
from DateTime import DateTime
import transaction

from Acquisition import aq_inner
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.security import checkPermission
from zc.relation.interfaces import ICatalog
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides
import logging


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
            # 太龐大，只找3筆
            if len(result) > 3:
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


class WithoutPT(BrowserView):
    """ Without PT View
    """


class TestZZZ(BrowserView):
    """ TestZZZ
    """
    logger = logging.getLogger("TestZZZ")

    def __call__(self):
        context = self.context
        request = self.request
        alsoProvides(request, IDisableCSRFProtection)

        catalog = context.portal_catalog

        brain = catalog(Type=['CPC', 'Notice', 'Organization'], review_state='private')
        pubCount = 0

        self.logger.info('一共有：%s' % len(brain))
        for item in brain:
            api.content.transition(obj=item.getObject(), transition='publish')
            transaction.commit()
            pubCount += 1

            if pubCount % 200 == 0:
                api.portal.send_email(recipient='andy@mingtak.com.tw',
                    sender='andy@mingtak.com.tw',
                    subject="主站已完成commit: %s" % pubCount,
                    body="As title",
                )
                transaction.commit()
        return

