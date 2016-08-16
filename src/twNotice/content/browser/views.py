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


class UpdateTraceNotice(BrowserView):
    """ Update Trace Notice
    """

    def __call__(self):
        context = self.context
        request = self.request
        portal = api.portal.get()
        alsoProvides(request, IDisableCSRFProtection)

        if api.user.is_anonymous():
            return '請先登入網站'

        currentId = api.user.get_current().id
        profile = portal['members'][currentId]

        if not request.form.get('id', '').strip():
            return 'flase'
        notice = api.content.find(type='Notice', id=request.form['id'])[0]
        noticeTraceCode = notice.noticeTraceCode

        if request.form.get('trace') == 'n':
            if not profile.noticeTraceCode:
                return '標案追蹤'
            elif noticeTraceCode in profile.noticeTraceCode:
                profile.noticeTraceCode.remove(noticeTraceCode)
            return '標案追蹤'

        elif request.form.get('trace') == 'y':
            if profile.noticeTraceCode:
                if noticeTraceCode in profile.noticeTraceCode:
                    return '取消追蹤'
                else:
                    profile.noticeTraceCode.append(noticeTraceCode)
            else:
                profile.noticeTraceCode = [noticeTraceCode]

            return '取消追蹤'


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

    def related_notice(self):
        context = self.context
        portal = api.portal.get()
        catalog = context.portal_catalog

#        brain = catalog({'Type':'Notice', 'cpc':context.id}, sort_on='dateString', sort_order='reverse')
        brain = api.content.find(type='Notice',
            cpc=context.id,
            context=portal['recent'],
            sort_on='dateString',
            sort_order='reverse')
        return brain


    def __call__(self):
        context = self.context
#        self.back_ref = back_references(context, 'cpc')
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

