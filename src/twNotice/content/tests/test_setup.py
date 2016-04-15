# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from twNotice.content.testing import TWNOTICE_CONTENT_INTEGRATION_TESTING  # noqa
from plone import api

import unittest


class TestSetup(unittest.TestCase):
    """Test that twNotice.content is properly installed."""

    layer = TWNOTICE_CONTENT_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if twNotice.content is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'twNotice.content'))

    def test_browserlayer(self):
        """Test that ITwnoticeContentLayer is registered."""
        from twNotice.content.interfaces import (
            ITwnoticeContentLayer)
        from plone.browserlayer import utils
        self.assertIn(ITwnoticeContentLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = TWNOTICE_CONTENT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['twNotice.content'])

    def test_product_uninstalled(self):
        """Test if twNotice.content is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'twNotice.content'))

    def test_browserlayer_removed(self):
        """Test that ITwnoticeContentLayer is removed."""
        from twNotice.content.interfaces import ITwnoticeContentLayer
        from plone.browserlayer import utils
        self.assertNotIn(ITwnoticeContentLayer, utils.registered_layers())
