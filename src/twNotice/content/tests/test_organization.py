# -*- coding: utf-8 -*-
from plone.app.testing import TEST_USER_ID
from zope.component import queryUtility
from zope.component import createObject
from plone.app.testing import setRoles
from plone.dexterity.interfaces import IDexterityFTI
from plone import api

from twNotice.content.testing import TWNOTICE_CONTENT_INTEGRATION_TESTING  # noqa
from twNotice.content.interfaces import IOrganization

import unittest2 as unittest


class OrganizationIntegrationTest(unittest.TestCase):

    layer = TWNOTICE_CONTENT_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='Organization')
        schema = fti.lookupSchema()
        self.assertEqual(IOrganization, schema)

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='Organization')
        self.assertTrue(fti)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='Organization')
        factory = fti.factory
        obj = createObject(factory)
        self.assertTrue(IOrganization.providedBy(obj))

    def test_adding(self):
        self.portal.invokeFactory('Organization', 'Organization')
        self.assertTrue(
            IOrganization.providedBy(self.portal['Organization'])
        )
