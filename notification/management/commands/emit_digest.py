from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.template import Context
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site

# favour django-mailer but fall back to django.core.mail
from django.core.mail import EmailMessage, SMTPConnection
from notification.models import Notice, DIGEST_MEDIUM, should_send

class Command(NoArgsCommand):
    help = "send digest emails for all users."
    
    def handle_noargs(self, **options):
        current_site = Site.objects.get_current()
        # use low level SMTP object to improve performance
        smtp = SMTPConnection()
        smtp.open()
        for user in User.objects.filter(email__isnull=False):
            notices = []
            for notice in Notice.objects.notices_for(user):
                if should_send(user, notice.notice_type, DIGEST_MEDIUM):
                    notices.append(notice.message)
                    notice.archive()
            if notices:
                import pdb
                # pdb.set_trace()
                context = Context({'notices': notices, 'user': user})
                body =  render_to_string ('notification/digest_email_body.html', context_instance=context)
                subject = render_to_string ('notification/digest_email_subject.txt', {'count': len(notices)}) 
                msg = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email])
                msg.content_subtype = "html"  # Main content is now text/html
                smtp._send(msg)
        smtp.close()    