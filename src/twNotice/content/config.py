# -*- coding: utf-8 -*-
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from twNotice.content import _


# 工程類 / 財物類 / 勞務類
NOTICE_TYPE = SimpleVocabulary(
    [SimpleTerm(value=u'engineering', title=_(u'engineering')),
     SimpleTerm(value=u'asset', title=_(u'asset')),
     SimpleTerm(value=u'service', title=_(u'service'))]
    )

NOTICE_SCOPE = [
    u'機關代碼',
    u'機關名稱',
    u'單位名稱',
    u'機關地址',
    u'聯絡人',
    u'聯絡電話',
    u'傳真號碼',
    u'電子郵件信箱',
    u'標案案號',
    u'標案名稱',
    u'標的分類',
    u'財物採購性質',
    u'採購金額級距',
]

GET_HEADERS = {
    "Accept-Language": "en-US,en;q=0.5",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "http://web.pcc.gov.tw",
    "Connection": "keep-alive"
}

URLLIB2_HEADER = [
    ("Accept-Language", "en-US,en;q=0.5"),
    ("User-Agent", "Mozilla/5.0 (Windows NT 10.0; WOW64; rv,40.0) Gecko/20100101 Firefox/40.0"),
    ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"),
    ("Referer", "http,//web.pcc.gov.tw"),
    ("Connection", "keep-alive"),
]
