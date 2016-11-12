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
        historyFolder = '/home/playgroup/HistoryNotice'
#        brain = api.content.find(Type='Folder', context=self.portal['notice'])

        delCount = 0
        for item in self.portal['notice'].getChildNodes():
            print 'DELETE: %s' % item.absolute_url()
            import pdb; pdb.set_trace()
            self.portal['notice'].manage_delObjects([item.getId()])
#            api.content.delete(obj=item)
            delCount += 1
            print delCount
            transaction.commit()


instance = DelOldNotice(sys.argv[3], sys.argv[4])
instance.del_old_notice()
