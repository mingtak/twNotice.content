from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
#from zope.component import getMultiAdapter
from plone import api


class SearchResult(BrowserView):

    template = ViewPageTemplateFile("template/search_result.pt")

    def __call__(self):
        context = self.context
        request = self.request
        catalog = context.portal_catalog
        self.portal = api.portal.get()

        if type(request.form.get('key')) == type(''):
            self.brain = catalog({'Type':'Product',
                                  'SearchableText':request.form['key'],
                                  'review_state':'published',})
        elif type(request.form.get('key')) == type([]):
            self.brain = catalog({'Type':'Product',
                                  'brand':request.form['key'],
                                  'review_state':'published',})

        return self.template()

