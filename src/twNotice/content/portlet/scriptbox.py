from plone.app.portlets.portlets import base
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.interface import implements
from twNotice.content import _


class IScriptbox(IPortletDataProvider):

    text = schema.Text(
        title=_(u"Script"),
        required=True,
        )


class Assignment(base.Assignment):
    implements(IScriptbox)

    def __init__(self, text=''):
        self.text = text

    @property
    def title(self):
        return _(u"Scriptbox")


class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('scriptbox.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    def render(self):
        return xhtml_compress(self._template())


class AddForm(base.AddForm):
    schema = IScriptbox
    label = _(u"Add Scriptbox Portlet")
    description = _(u"This portlet rendering Scriptbox.")

    def create(self, data):
        return Assignment(
            text=data.get('text', ''),
            )


class EditForm(base.EditForm):
    schema = IScriptbox
    label = _(u"Edit Scriptbox Portlet")
    description = _(u"This portlet rendering Scriptbox.")

