from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
#from zope.component import getMultiAdapter
from plone import api
from DateTime import DateTime
import transaction


class CoverView(BrowserView):
    """ Cover View
    """
    index = ViewPageTemplateFile("template/cover_view.pt")

    def __call__(self):
        return self.index()
