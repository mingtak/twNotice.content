# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
#from zope.component import getMultiAdapter
from plone import api
import urllib2
import csv
from bs4 import BeautifulSoup
from z3c.relationfield.relation import RelationValue
from zope import component
from zope.app.intid.interfaces import IIntIds
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
from DateTime import DateTime
import transaction
import logging
from Products.CMFPlone.utils import safe_unicode


logger = logging.getLogger("twNotice.content.import_cpc")


class ImportCPC(BrowserView):
    """ Import CPC
    """
    def __call__(self):
        context = self.context
        request = self.request
        response = request.response
        catalog = context.portal_catalog
        portal = api.portal.get()
        intIds = component.getUtility(IIntIds)


        with open('/home/playgroup/CpcOpenData.xml') as file:
            soup = BeautifulSoup(file.read(), 'xml')

        for item in soup.find_all('object'):
#            import pdb;pdb.set_trace()
            cpc = api.content.create(
                type='CPC',
                id=unicode(item.code.string),
                title=unicode(item.cname.string),
                engTitle=unicode(item.ename.string),
                noticeCategory=unicode(item.category.string),
                container=portal['resource']['category']
            )
            cpc.childrenCPC = {cpc.id:cpc.title}
            if item.cpcsub.string:
                for cpcsub in item.cpcsub.string.split(','):
                    key = cpcsub.split(' ')[0]
                    value = cpcsub.split(' ')[1]
                    cpc.childrenCPC[key] = value
            cpc.reindexObject('childrenCPC')
            logger.info(cpc.title)

        transaction.commit()
