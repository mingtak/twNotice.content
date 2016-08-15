# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
#from zope.component import getMultiAdapter
from plone import api
import transaction
#from zope.security import checkPermission


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
        reqeust = self.request

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
        return self.template()
