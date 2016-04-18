# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from twNotice.content import _
from zope import schema
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from z3c.relationfield.schema import RelationChoice
from plone.app.vocabularies.catalog import CatalogSource

class ITwnoticeContentLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


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
