# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
#from zope.component import getMultiAdapter
from plone import api
from Products.CMFPlone.utils import safe_unicode
from DateTime import DateTime


class SearchResult(BrowserView):

    template = ViewPageTemplateFile("template/search_result.pt")

    def __call__(self):
        context = self.context
        request = self.request
        catalog = context.portal_catalog
        self.portal = api.portal.get()
        self.safe_unicode = safe_unicode
        container = self.portal['recent']

        queryString={'Type':'Notice'}

        path = '/'.join(container.getPhysicalPath())
        queryString['path'] = path

        org_name = request.form.get('org_name')
        pccOrgCode_set = []

        if org_name: # and len(safe_unicode(org_name)) >= 3: ###
            orgSet = catalog(Title=org_name, Type='Organization')
            if orgSet:
                for org in orgSet:
                    pccOrgCode_set.append(org.pccOrgCode)
                if pccOrgCode_set:
                    queryString['pccOrgCode'] = pccOrgCode_set

        queryString['Title'] = request.form.get('keyword')
        if not queryString['Title']:
            queryString['Title'] = '採購'

        max_budget = 0 if not request.form.get('max_budget', ' ').isdigit() else int(request.form.get('max_budget'))
        min_budget = 0 if not request.form.get('min_budget', ' ').isdigit() else int(request.form.get('min_budget'))
        if min_budget or max_budget:
            if not min_budget:
                queryString['budget'] = {'query':max_budget, 'range':'max'}
            elif not max_budget:
                queryString['budget'] = {'query':min_budget, 'range':'min'}
            else:
                queryString['budget'] = {'query':[min_budget, max_budget], 'range':'min:max'}

        date_range = request.form.get('date_range')
        if date_range == '3days':
            startDate = DateTime() - 3
        elif date_range == 'week':
            startDate = DateTime() - 7
        elif date_range == 'month':
            startDate = DateTime() - 30
        else:
            startDate = DateTime() - 1

        queryString['created'] = {'query':(startDate), 'range': 'min'}

        self.brain = catalog(
            Title=queryString.get('Title'),
            pccOrgCode=queryString.get('pccOrgCode'),
            budget=queryString.get('budget'),
            created=queryString['created'],
            path=queryString['path'],
            sort_on='created',
            sort_order='reverse',
        )

        return self.template()

