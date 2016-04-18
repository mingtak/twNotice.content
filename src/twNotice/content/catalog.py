# -*- coding: utf-8 -*-
from plone.indexer.decorator import indexer
from zope.interface import Interface
from Products.CMFPlone.utils import safe_unicode

from twNotice.content.interfaces import IOrganization, ICPC


@indexer(ICPC)
def noticeCategory_indexer(obj):
    return obj.noticeCategory

@indexer(ICPC)
def childrenCPC_indexer(obj):
    return obj.childrenCPC.keys()

@indexer(IOrganization)
def orgCode_indexer(obj):
    return obj.orgCode

@indexer(IOrganization)
def pccOrgCode_indexer(obj):
    return obj.pccOrgCode

@indexer(IOrganization)
def address_indexer(obj):
    return obj.address

""" example
@indexer()
def _indexer(obj):
    return obj.
"""
