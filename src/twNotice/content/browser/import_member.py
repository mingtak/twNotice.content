# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from plone import api
import random
from DateTime import DateTime
import time
from Products.CMFPlone.utils import safe_unicode
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides
import csv
import logging
import transaction


logger = logging.getLogger("ImportMember")

class ImportMember(BrowserView):
    """ Import Member
    """

    def __call__(self):
        context = self.context
        request = self.request
        catalog = context.portal_catalog
        portal = api.portal.get()
        alsoProvides(request, IDisableCSRFProtection)

        with open("/home/playgroup/member.csv", "rb") as file:
            members = csv.DictReader(file)

            count = 0
            for item in members:

                if not item.get('id'):
                    continue

                user = api.user.get(userid='fb%s' % item.get('id'))
                if not user:
                    email = item.get('email')
                    if not email:
                        randString = str(random.randint(0, 100000))
                        email = 'rand%s%s@opptoday.com' % (DateTime().strftime('%s'), randString)
#                    import pdb; pdb.set_trace()
                    try:
                        user = api.user.create(
                                   email=email,
                                   username='fb%s' % item.get('id'),
                                   roles=('Member', ),
                                   properties={'fullname': item.get('name')}
                               )
                    except:
                        randString = str(random.randint(0, 100000))
                        email = 'rand%s%s@opptoday.com' % (DateTime().strftime('%s'), randString)
                        user = api.user.create(
                                   email=email,
                                   username='fb%s' % item.get('id'),
                                   roles=('Member', ),
                                   properties={'fullname': item.get('name')}
                               )

                if self.confirmProfile(item.get('id')):
                    continue

                with api.env.adopt_user(user=user):
                    with api.env.adopt_roles(['Manager']):
                        try:
                            profile = api.content.create(
                                type='Profile',
                                container=portal['members'],
                                id='fb%s' % item.get('id'),
                                title=item.get('name'),
                                email=item.get('email'),
                                subscribe=True if item.get('subscribe') == 'True' else False,
                            )
                            profile.traceKeywords = []
                        except:continue

                        for keyword in item.get('keywords').split():
                            profile.traceKeywords.append(keyword)

                count += 1
                if not (count % 100):
                    transaction.commit()
                    logger.info('Add profile: %s' % count)


    def confirmProfile(self, id):
        return api.content.find(Type='Profile', id='fb%s' % id)
