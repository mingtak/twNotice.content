# -*- coding: utf-8 -* 
from twNotice.content import _
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
#from zope.component import getMultiAdapter

from z3c.relationfield.relation import RelationValue
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

from plone import api
from pyallpay import AllPay
from DateTime import DateTime
import random
import transaction

import logging


class ReturnUrl(BrowserView):
    """ Return URL
    """

    def __call__(self):
        context = self.context


class ClientBackUrl(BrowserView):
    """ Client back url
    """

#    template = ViewPageTemplateFile("template/client_back_url.pt")
    def __call__(self):
        context = self.context


class Checkout(BrowserView):
    """ Checkout
    """

    logger = logging.getLogger('bill.Checkout')
    template = ViewPageTemplateFile("template/checkout.pt")

    def __call__(self):
        context = self.context


class InvoiceMethod(BrowserView):
    """ Invoice Method
    """

    logger = logging.getLogger('bill.InvoiceMethod')
    template = ViewPageTemplateFile("template/invoice_method.pt")

    def __call__(self):
        context = self.context
