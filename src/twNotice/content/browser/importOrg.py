# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
#from zope.component import getMultiAdapter
from plone import api
import csv
from z3c.relationfield.relation import RelationValue
from zope import component
from zope.app.intid.interfaces import IIntIds
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent, ObjectModifiedEvent
from DateTime import DateTime
import transaction
import logging


logger = logging.getLogger("twNotice.content.import_org")

class ImportOrg(BrowserView):
    """ Import Org, 每次匯入，必須執行二次，csv檔標頭要改好才可以
    """
    def __call__(self):
        context = self.context
        request = self.request
        response = request.response
        catalog = context.portal_catalog
        portal = api.portal.get()
        intIds = component.getUtility(IIntIds)

        with open('/home/playgroup/orglist.csv') as file:
            csvData = csv.DictReader(file)

            for row in csvData:
              try:
                if row.get('unitLevel') == '1':
                    row['parentOrgCode'] = ''
                if row.get('orgCode') == row.get('oldOrgCode'):
                    row['oldOrgCode'] = ''
                if row.get('orgCode') == row.get('newOrgCode'):
                    row['newOrgCode'] = ''

                pccOrgCode = ''
                for level in range(5):
                    if level == 0:
                        pccOrgCode += row.get('orgCode')[0]
                    elif int(row.get('orgCode')[level*2-1:-1]) == 0:
                        break
                    elif row.get('orgCode')[level*2-1:level*2+1] == '00' and int(row.get('orgCode')[level*2+1:-1]) > 0:
                        pccOrgCode += '.100'
                    else:
                        pccOrgCode += ('.' + str(int(row.get('orgCode')[level*2-1:level*2+1])))
                if not api.content.find(id=row['orgCode']):
                    obj = api.content.create(
                        type='Organization',
                        id=row['orgCode'],
                        title=row['title'],
                        orgCode=row['orgCode'],
                        pccOrgCode=pccOrgCode,
                        address=row['address'],
                        container=portal['resource']['organization'],
                    )
                    if api.content.find(id=row['newOrgCode']):
                        obj.newOrg = RelationValue(intIds.getId(portal['resource']['organization'][row['newOrgCode']]))
                    if api.content.find(id=row['oldOrgCode']):
                        obj.oldOrg = RelationValue(intIds.getId(portal['resource']['organization'][row['oldOrgCode']]))
                    if api.content.find(id=row['parentOrgCode']):
                        obj.parentOrg = RelationValue(intIds.getId(portal['resource']['organization'][row['parentOrgCode']]))
                    notify(ObjectModifiedEvent(obj))
                    logger.info('OK, %s' % obj.title)
                # update content
                else:
                    obj = portal['resource']['organization'][row['orgCode']]
                    if api.content.find(id=row['newOrgCode']):
                        obj.newOrg = RelationValue(intIds.getId(portal['resource']['organization'][row['newOrgCode']]))  
                    if api.content.find(id=row['oldOrgCode']):
                        obj.oldOrg = RelationValue(intIds.getId(portal['resource']['organization'][row['oldOrgCode']]))
                    if api.content.find(id=row['parentOrgCode']):
                        obj.parentOrg = RelationValue(intIds.getId(portal['resource']['organization'][row['parentOrgCode']]))
                    notify(ObjectModifiedEvent(obj))
                    logger.info('OK, %s' % obj.title)
                transaction.commit()
              except:
                if row.get('unitLevel') == '1':
                    row['parentOrgCode'] = ''
                if row.get('orgCode') == row.get('oldOrgCode'):
                    row['oldOrgCode'] = ''
                if row.get('orgCode') == row.get('newOrgCode'):
                    row['newOrgCode'] = ''

                if not api.content.find(id=row['orgCode']):
                    obj = api.content.create(
                        type='Organization',
                        id=row['orgCode'],
                        title=row['title'],
                        orgCode=row['orgCode'],
                        address=row['address'],
                        container=portal['resource']['organization'],
                    )
                    if api.content.find(id=row['newOrgCode']):
                        obj.newOrg = RelationValue(intIds.getId(portal['resource']['organization'][row['newOrgCode']]))
                    if api.content.find(id=row['oldOrgCode']):
                        obj.oldOrg = RelationValue(intIds.getId(portal['resource']['organization'][row['oldOrgCode']]))
                    if api.content.find(id=row['parentOrgCode']):
                        obj.parentOrg = RelationValue(intIds.getId(portal['resource']['organization'][row['parentOrgCode']]))
                    notify(ObjectModifiedEvent(obj))
                    logger.info('OK, %s' % obj.title)
                # update content
                else:
                    obj = portal['resource']['organization'][row['orgCode']]
                    if api.content.find(id=row['newOrgCode']):
                        obj.newOrg = RelationValue(intIds.getId(portal['resource']['organization'][row['newOrgCode']]))
                    if api.content.find(id=row['oldOrgCode']):
                        obj.oldOrg = RelationValue(intIds.getId(portal['resource']['organization'][row['oldOrgCode']]))
                    if api.content.find(id=row['parentOrgCode']):
                        obj.parentOrg = RelationValue(intIds.getId(portal['resource']['organization'][row['parentOrgCode']]))
                    notify(ObjectModifiedEvent(obj))
                    logger.info('OK, %s' % obj.title)
                transaction.commit()
                pass
              ## logger
