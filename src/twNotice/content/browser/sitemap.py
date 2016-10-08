# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize import ram
from time import time


class SiteMap1(BrowserView):
    """ SiteMap1
    """

    index = ViewPageTemplateFile('template/sitemap.pt')

    @ram.cache(lambda *args: time() // (60 * 60 * 4))
    def __call__(self):
        context = self.context
        catalog = context.portal_catalog

        self.brain = catalog(Type='Notice', sort_on='modified', sort_order='reverse')[:50000]
        return self.index()


class SiteMap2(SiteMap1):
    """ SiteMap2
    """

    @ram.cache(lambda *args: time() // (60 * 60 * 4))
    def __call__(self):
        context = self.context
        catalog = context.portal_catalog

        self.brain = catalog({'Type':['Document', 'Product', 'News Item', 'Folder', 'Page']},
                              sort_on='modified',
                              sort_order='reverse')[:50000]
        return self.index()

