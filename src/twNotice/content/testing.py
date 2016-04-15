# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import twNotice.content


class TwnoticeContentLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=twNotice.content)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'twNotice.content:default')


TWNOTICE_CONTENT_FIXTURE = TwnoticeContentLayer()


TWNOTICE_CONTENT_INTEGRATION_TESTING = IntegrationTesting(
    bases=(TWNOTICE_CONTENT_FIXTURE,),
    name='TwnoticeContentLayer:IntegrationTesting'
)


TWNOTICE_CONTENT_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(TWNOTICE_CONTENT_FIXTURE,),
    name='TwnoticeContentLayer:FunctionalTesting'
)


TWNOTICE_CONTENT_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        TWNOTICE_CONTENT_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='TwnoticeContentLayer:AcceptanceTesting'
)
