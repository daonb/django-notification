from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
# favour django-mailer but fall back to django.core.mail
from django.core.mail import EmailMessage, SMTPConnection
from notification.model import Notice, DIGEST_MEDIUM, should_send

EMAIL_SUBJECT = getattr(settings, 'NOTIFICATION_DIGEST_SUBJECT', _('%(site_name)s - %(count)s new notices - digested'))
class Command(NoArgsCommand):
    help = "Emit digest emails."
    
    def handle_noargs(self, **options):
        current_site = Site.objects.get_current()
        # use low level SMTP object to improve performance
        smtp = SMTPConnection()
        smtp.open()
        for user in User.objects.filter(email__isnull=False):
            n = []
            for notice in Notice.objects.notices_for(user):
                if should_send(user, notice.notice_type, DIGEST_MEDIUM):
                    n.append(notice.message)
                    notice.archive()
            body = '<br />'.join(n)
            subject = EMAIL_SUBJECT % dict(site_name=current_site.name, count=len(n))
            msg = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email])
            msg.content_subtype = "html"  # Main content is now text/html
            smtp._send(msg)
        smtp.close()    