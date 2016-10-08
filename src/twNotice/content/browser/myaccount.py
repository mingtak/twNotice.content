# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
#from zope.component import getMultiAdapter
from plone import api
import transaction
#from zope.security import checkPermission
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides


class BaseMethod(BrowserView):
    """ Base Method """

    def currentId(self):
        if api.user.is_anonymous():
            return None
        return api.user.get_current().id


    def memberGrade(self):
        if api.user.get_current() in api.user.get_users(groupname='paid'):
            return '付費帳號'
        else:
            return '一般帳號'


    def myProfile(self):
        portal = api.portal.get()
        request = self.request

        try:
            return portal['members'][api.user.get_current().id]
        except:
            request.response.redirect('/')
        return


class AccountInfo(BaseMethod):
    """ Account Information
    """
    template = ViewPageTemplateFile("template/account_info.pt")

    def __call__(self):
        context = self.context
        request = self.request

        if api.user.is_anonymous():
            return request.recdirect(context.absolute_url())

        return self.template()


class UpdateAccountInfo(BaseMethod):
    """ Update Account Information
    """

    def update_basic(self, profile, request):
        profile.title = request.form.get('name')
        profile.phone = request.form.get('phone')
        profile.cellPhone = request.form.get('cellPhone')
        profile.addr_district = request.form.get('district')
        profile.addr_city = request.form.get('city')
        profile.addr_zip = request.form.get('zipcode')
        profile.addr_address = request.form.get('address')
        profile.email = request.form.get('email')
        return


    def update_keyword(self, profile, request):
        profile.subscribe = request.form.get('subscribe', False)

        keywords = request.form.get('keyword')
        if not keywords:
            profile.traceKeywords = None
            return

        profile.traceKeywords = []

        if type(keywords) == type(''):
            profile.traceKeywords.append(keywords)
        else:
            for keyword in keywords:
                if keyword.strip():
                    profile.traceKeywords.append(keyword)
        return


    def __call__(self):
        context = self.context
        request = self.request
        portal = api.portal.get()
        alsoProvides(request, IDisableCSRFProtection)

        currentId = self.currentId()
        profile = portal['members'][currentId]

        if request.form.has_key('modkeyword'):
            self.update_keyword(profile, request)
        elif request.form.has_key('modbasic'):
            self.update_basic(profile, request)

        request.response.redirect('%s/@@account_info' % portal.absolute_url())

        return

