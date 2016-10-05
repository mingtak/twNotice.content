# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from DateTime import DateTime
import logging
from Products.CMFPlone.utils import safe_unicode
from email_validator import validate_email, EmailNotValidError
from email.mime.text import MIMEText


logger = logging.getLogger("SendMail")

# TODO:速報-提供第二次以後公告

class BaseMethod(BrowserView):
    """ Base Method
    """

    def getCurrentId(self):
        if api.user.is_anonymous():
            return None
        return api.user.get_current().id


    def validateEmail(self, email):
        try:
            result = validate_email(email) # validate and get info
            email = result["email"] # replace with normalized form
        except:
            return False
        return email


class SendNotice(BaseMethod):
    """ Import Recent
    """

    def __call__(self):
        context = self.context
        request = self.request
        response = request.response
        catalog = context.portal_catalog
        portal = api.portal.get()
#        alsoProvides(request, IDisableCSRFProtection)

        profiles = portal['members'].getChildNodes()

        end = DateTime() + 0.1 # If we have some clock skew peek a little to the future
        start = DateTime() - 0.6
        created_date_range = {'query':(start,end), 'range':'min:max'}
        for profile in profiles:
            if not profile.traceKeywords:
                continue

            email = self.validateEmail(profile.email)
            if not email:
                logger.Error('Invalid Email Address: %s' % profile.email)
                continue

            result = []
            noticeURLs = []
            for keyword in profile.traceKeywords:
                brain = list(api.content.find(context=portal['recent'],
                    created=created_date_range,
                    Title=keyword,
                    sort_on='pccOrgCode'))
                while brain:
                    if brain[0].noticeURL in noticeURLs:
                        brain.remove(brain[0])
                        continue
                    result.append(brain[0])
                    noticeURLs.append(brain[0].noticeURL)
                    brain.remove(brain[0])

            count = 0
            html = '<strong>目前共有 %s 筆符合的公告，您目前的追蹤關鍵字:</strong><p>%s</p>' % (len(result), ' / '.join(profile.traceKeywords).encode('utf-8'))
            for item in result:
                html += '<li><a href=%s>%s</a></li>' % (item.getURL(), item.Title)
                count += 1

                show = 100 if api.group.get(groupname='paid') in api.group.get_groups(username=profile.id) else 10
                if count >= show:
                    html += '<p><a href=%s/@@today_notice>更多符合的公告內容，請上網查看</a></p>' % portal.absolute_url()
                    break

            mimeBody = MIMEText('%s' % html, 'html', 'utf-8')

            api.portal.send_email(recipient=profile.email,
                sender='service@mingtak.com.tw',
                subject=u'%s您好，今日商機王-政府採購公告：%s' % (safe_unicode(profile.title), str(DateTime()).split()[0]),
                body='%s' % (mimeBody.as_string()))
        return


class TodayNotice(BaseMethod):

    index = ViewPageTemplateFile('template/today_notice.pt')

    def __call__(self):
        context = self.context
        request = self.request
        response = request.response
        catalog = context.portal_catalog
        portal = api.portal.get()

        currentId = self.getCurrentId()
        if not currentId:
            # TODO:不是redirect，是要求登入
            response.redirect(portal.absolute_url())
            return
        self.profile = portal['members'][currentId]

        end = DateTime() + 0.1 # If we have some clock skew peek a little to the future
        start = DateTime() - 1
        created_date_range = {'query':(start,end), 'range':'min:max'}

        traceKeywords = self.profile.traceKeywords
        if not traceKeywords:
            response.redirect('%s/account_info' % portal.absolute_url())
            return


        self.result = []
        noticeURLs = []
        for keyword in traceKeywords:
            brain = list(api.content.find(context=portal['recent'],
                created=created_date_range,
                Title=keyword,
                sort_on='pccOrgCode'))
            while brain:
                if brain[0].noticeURL in noticeURLs:
                    brain.remove(brain[0])
                    continue
                self.result.append(brain[0])
                noticeURLs.append(brain[0].noticeURL)
                brain.remove(brain[0])
        return self.index()
