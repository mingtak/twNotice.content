from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
#from zope.component import getMultiAdapter
from plone import api
import transaction
#from Acquisition import aq_inner
#from zope.component import getUtility
#from zope.intid.interfaces import IIntIds
#from zope.security import checkPermission
#from zc.relation.interfaces import ICatalog


class AccountInfo(BrowserView):
    """ Account Information
    """
    template = ViewPageTemplateFile("template/account_info.pt")

    def __call__(self):
        context = self.context
