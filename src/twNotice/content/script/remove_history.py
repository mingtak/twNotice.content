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

from Products.CMFCore.utils import getToolByName
from Products.CMFEditions.utilities import dereference



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

        print 'Start'
        policy = getToolByName(self.portal, 'portal_purgepolicy')
        catalog = getToolByName(self.portal, 'portal_catalog')

        removeCount = 0
        for count, brain in enumerate(catalog()):
            obj = brain.getObject()
            obj, history_id = dereference(obj)
            if history_id is not None:
                policy.beforeSaveHook(history_id, obj)
                print 'purged object %s: %s' % (count, obj.absolute_url_path())
                removeCount += 1
                if removeCount == 1000:
                    break

            if not count % 10000:
                print count

        transaction.commit()
        return


instance = DelOldNotice(sys.argv[3], sys.argv[4])
instance.del_old_notice()

