# -*- coding: utf-8 -*-
from plone.indexer.decorator import indexer
from zope.interface import Interface
from Products.CMFPlone.utils import safe_unicode
import re
from twNotice.content.interfaces import IOrganization, ICPC, INotice


@indexer(INotice)
def noticeTimes_indexer(obj):
    try:
        if obj.noticeMeta.get(u'新增公告傳輸次數'):
            return int(obj.noticeMeta.get(u'新增公告傳輸次數'))
        elif obj.noticeMeta.get(safe_unicode('新增公告傳輸次數')):
            return int(obj.noticeMeta.get(safe_unicode('新增公告傳輸次數')))
    except:
        return None

@indexer(INotice)
def cpc_indexer(obj):
    return obj.cpc.to_object.id

@indexer(INotice)
def budget_indexer(obj):
    """
    budget = re.findall('[0-9]+', obj.noticeMeta.get(safe_unicode("預算金額")))

    if budget:
        d = ''
        for digit in budget:
            d += digit
        return int(d)
    """
    try:
        budget = int(filter(unicode.isdigit, obj.noticeMeta.get(safe_unicode('預算金額'), '0')))
    except:
        budget = int(filter(str.isdigit, obj.get(safe_unicode('預算金額'), '0')))
    return budget


@indexer(INotice)
def winner_indexer(obj):
    keyIndex = 1
    winner = []
    if obj.noticeMeta.get(u"得標廠商"):
        winner.append(obj.noticeMeta.get(u"得標廠商"))
    while True:
        if obj.noticeMeta.get(u"得標廠商_%s" % keyIndex):
            winner.append(obj.noticeMeta.get(u"得標廠商_%s" % keyIndex))
            keyIndex += 1
            continue
        else:
            break
    return winner

@indexer(INotice)
def bidders_indexer(obj):
    keyIndex = 1
    bidders = []
    if obj.noticeMeta.get(u"廠商名稱"):
        bidders.append(obj.noticeMeta.get(u"廠商名稱"))
    while True:
        if obj.noticeMeta.get(u"廠商名稱_%s" % keyIndex):
            bidders.append(obj.noticeMeta.get(u"廠商名稱_%s" % keyIndex))
            keyIndex += 1
            continue
        else:
            break
    return bidders

@indexer(INotice)
def dateString_indexer(obj):
    return obj.dateString

@indexer(INotice)
def noticeTraceCode_indexer(obj):
    return '%s--%s' % (obj.noticeMeta.get(u'機關代碼'), obj.noticeMeta.get(u'標案案號'))

@indexer(INotice)
def noticeType_indexer(obj):
    return obj.noticeType

@indexer(INotice)
def noticeURL_indexer(obj):
    return obj.noticeURL

@indexer(ICPC)
def noticeCategory_indexer(obj):
    return obj.noticeCategory

@indexer(ICPC)
def childrenCPC_indexer(obj):
    return obj.childrenCPC.keys()

@indexer(IOrganization)
def orgCode_indexer(obj):
    return obj.orgCode

@indexer(INotice)
def pccOrgCode_notice_indexer(obj):
    return obj.noticeMeta.get(u'機關代碼')

@indexer(IOrganization)
def pccOrgCode_org_indexer(obj):
    return obj.pccOrgCode

@indexer(IOrganization)
def address_indexer(obj):
    return obj.address

""" example
@indexer()
def _indexer(obj):
    return obj.
"""
