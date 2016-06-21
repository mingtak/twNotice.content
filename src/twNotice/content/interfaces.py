# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from twNotice.content import _
from zope import schema
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from plone.app.vocabularies.catalog import CatalogSource
from .config import NOTICE_TYPE


class ITwnoticeContentLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class ICover(Interface):
    """ 首頁 """
    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )

    heros = RelationList(
        title=_(u"Heros"),
        description=_(u"Rleated image for hero section"),
        value_type=RelationChoice(title=_(u"Related"),
                                  source=CatalogSource(Type='Image'),),
        required=False,
    )

    hotNews = RelationList(
        title=_(u"Hot News"),
        description=_(u"Hot news for home page"),
        value_type=RelationChoice(title=_(u"Related"),
                                  source=CatalogSource(Type='News Item'),),
        required=False,
    )


class INotice(Interface):
    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )

    description = schema.Text(
        title=_(u"Description"),
        required=False,
    )

    dateString = schema.TextLine(
        title=_(u"Date String"),
        required=True,
    )

    cpc = RelationChoice(
        title=_(u"Related CPC"),
        source=CatalogSource(Type='CPC'),
        required=False,
    )

    noticeType = schema.TextLine(
        title=_(u"Notice Type"),
        required=True,
    )

    noticeURL = schema.URI(
        title=_(u"Notice URL"),
        required=True,
    )

    noticeMeta = schema.Dict(
        title=_(u"Notice Metadata"),
        key_type=schema.TextLine(title=u"Key"),
        value_type=schema.TextLine(title=u"Value"),
        required=True,
    )


class ICPC(Interface):
    """ CPC Open data """
    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )

    description = schema.Text(
        title=_(u"Description"),
        required=False,
    )

    engTitle = schema.TextLine(
        title=_(u"English Title"),
        required=True,
    )

    noticeCategory = schema.TextLine(
        title=_(u"Notice Category"),
        required=True,
    )

    childrenCPC = schema.Dict(
        title=_(u"Children CPC"),
        key_type=schema.TextLine(title=u"Key"),
        value_type=schema.TextLine(title=u"Value"),
        required=False,
    )


class IOrganization(Interface):

    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )

    description = schema.Text(
        title=_(u"Description"),
        required=False,
    )

    address = schema.TextLine(
        title=_(u"Address"),
        required=False,
    )

    orgCode = schema.TextLine(
        title=_(u"Organization Code"),
        required=True,
    )

    pccOrgCode = schema.TextLine(
        title=_(u"PCC Organization Code"),
    )

    newOrg = RelationChoice(
        title=_(u"New Organization"),
        source=CatalogSource(Type='Organization'),
        required=False,
    )

    oldOrg = RelationChoice(
        title=_(u"Old Organization"),
        source=CatalogSource(Type='Organization'),
        required=False,
    )

    parentOrg = RelationChoice(
        title=_(u"Parent Organization"),
        source=CatalogSource(Type='Organization'),
        required=False,
    )


class IProfile(Interface):
    """ 個人頁面 """
    title = schema.TextLine(
        title=_(u"Profile Name"),
        required=True,
    )

    description = schema.Text(
        title=_(u"Description"),
        required=False,
    )

    phone = schema.TextLine(
        title=_(u"Phone"),
        description=_(u"Phone Number."),
        required=False,
    )

    cellPhone = schema.TextLine(
        title=_(u"Cell Phone"),
        description=_(u"Cell Phone number."),
        required=False,
    )

    email = schema.TextLine(
        title=_(u"Email"),
        description=_(u"Email."),
        required=False,
    )

    addr_city = schema.TextLine(
        title=_(u"City"),
        description=_(u"City name."),
        required=False,
    )

    addr_district = schema.TextLine(
        title=_(u"District"),
        description=_(u"District"),
        required=False,
    )

    addr_zip = schema.TextLine(
        title=_(u"ZIP Code"),
        description=_(u"ZIP code"),
        required=False,
    )

    addr_address = schema.TextLine(
        title=_(u"Address"),
        description=_(u"Address"),
        required=False,
    )
