# -*- coding: utf-8 -*-

import sys
from Testing import makerequest
from AccessControl.SecurityManagement import newSecurityManager
from zope.site.hooks import setHooks
from zope.site.hooks import setSite

from plone import api
from DateTime import DateTime
import transaction
import csv
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides
from bs4 import BeautifulSoup
from Products.CMFPlone.utils import safe_unicode
from plone.app.textfield.value import RichTextValue
from plone import namedfile
#import html2text
import urllib2
import logging
import os
import pickle

logger = logging.getLogger('Script(del_contents.py)')


class DelOldNotice:

    def __init__(self, portal, admin):
        root = makerequest.makerequest(app)
        self.portal = getattr(root, portal, None)
        if self.portal is None:
            logger.error('lost or wrong argv!')
            exit()

        admin = root.acl_users.getUserById(admin)
        admin = admin.__of__(self.portal.acl_users)
        newSecurityManager(None, admin)
        setHooks()
        setSite(self.portal)
        self.portal.setupCurrentSkin(self.portal.REQUEST)

    def del_old_notice(self):
        if DateTime().hour() in [7,8,9,10,12,14,16,18,20,22]:
            return

        historyFolder = '/home/playgroup/HistoryNotice'
        brain = api.content.find(Type='Notice', context=self.portal['notice'])

        delCount = 0
        for item in brain:
            if DateTime().hour() in [7,8,9,10,12,14,16,18,20,22]:
                break

            try:
                filename = filter(str.isalnum, item.noticeURL)
                if not os.path.exists('%s/%s' % (historyFolder, item.dateString)):
                    os.system('mkdir %s/%s' % (historyFolder, item.dateString))

                if os.path.exists('%s/%s/%s' % \
                                      (historyFolder,
                                       item.dateString,
                                       filename)):
                    continue

                notice = {
                    'title':item.Title,
                    'noticeType':item.noticeType,
                    'noticeURL':item.noticeURL,
                    'dateString':item.dateString,
                    'cpc': item.getObject().cpc.to_object.id,
                    'noticeMeta': dict(item.getObject().noticeMeta),
                    'noticeTimes':item.noticeTimes,
                    'budget':item.budget,
                    'winner':list(item.winner),
                    'bidders':list(item.bidders),
                    'noticeTraceCode':item.noticeTraceCode,
                    'pccOrgCode':item.pccOrgCode,
                }

                with open('%s/%s/%s' % \
                              (historyFolder,
                               item.dateString,
                               filename), 'w') as file:
                    pickle.dump(notice, file)

                print '%s: %s' % (DateTime(), item.Title)
                try:
                    api.content.delete(obj=item.getObject())
                    delCount += 1
                    if delCount % 100 == 0:
                        print delCount
                        transaction.commit()
                except:
                    import pdb; pdb.set_trace()
            except:pass


instance = DelOldNotice(sys.argv[3], sys.argv[4])
instance.del_old_notice()
