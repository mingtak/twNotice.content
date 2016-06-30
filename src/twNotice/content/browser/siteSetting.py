# -*- coding: utf-8 -*-
from twNotice.content import _
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper

from plone.z3cform import layout
from z3c.form import form
from plone.directives import form as Form
from zope import schema


class ISiteSetting(Form.Schema):

    welcomeWords = schema.TextLine(
        title=_(u"Welcome words"),
        required=False,
    )

    contactEmail = schema.TextLine(
        title=_(u"Contact Email"),
        required=False,
    )

    contactPhone = schema.TextLine(
        title=_(u"Contact Phone"),
        required=False,
    )

    footerInfo = schema.Text(
        title=_(u"Footer Information, support html tag"),
        required=False,
    )

    rReportPath = schema.TextLine(
        title=_(u"R Report folder Path at filesystem."),
        required=False,
    )

class SiteSettingControlPanelForm(RegistryEditForm):
    form.extends(RegistryEditForm)
    schema = ISiteSetting


SiteSettingControlPanelView = layout.wrap_form(SiteSettingControlPanelForm, ControlPanelFormWrapper)
SiteSettingControlPanelView.label = _(u"Site Setting")
