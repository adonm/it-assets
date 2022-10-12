from django.conf import settings
from django.core import mail
from django.core.management.base import BaseCommand, CommandError
import logging

from itassets.utils import ms_graph_client_token
from organisation.utils import ms_graph_subscribed_sku


class Command(BaseCommand):
    help = 'Checks Microsoft 365 product licence availability and sends a notification email when availability drops too low'

    def add_arguments(self, parser):
        parser.add_argument(
            '--emails',
            action='store',
            default=None,
            type=str,
            help='Comma-separated list of emails to which to send the notification (defaults to OIM Service Desk)',
            dest='emails',
        )
        parser.add_argument(
            '--threshold',
            action='store',
            default=None,
            type=int,
            help='Number of available licences at which to send the notification (default 5)',
            dest='threshold',
        )

    def handle(self, *args, **options):
        send_notification = False

        if options['emails']:
            try:
                recipients = options['emails'].split(',')
            except ValueError:
                raise CommandError('Invalid emails value: {} (use comma-separated string)'.format(options['emails']))
        else:
            recipients = [settings.SERVICE_DESK_EMAIL]

        if options['threshold']:
            threshold = options['threshold']
        else:
            threshold = settings.LICENCE_NOTIFY_THRESHOLD

        token = ms_graph_client_token()

        e5_sku = ms_graph_subscribed_sku(settings.M365_E5_SKU, token)
        e5_consumed = e5_sku['consumedUnits']
        e5_enabled = e5_sku['prepaidUnits']['enabled']
        if e5_enabled - e5_consumed <= threshold:
            send_notification = True

        f3_sku = ms_graph_subscribed_sku(settings.M365_F3_SKU, token)
        f3_consumed = f3_sku['consumedUnits']
        f3_enabled = f3_sku['prepaidUnits']['enabled']
        if f3_enabled - f3_consumed <= threshold:
            send_notification = True

        eo_sku = ms_graph_subscribed_sku("19ec0d23-8335-4cbd-94ac-6050e30712fa", token)  # EXCHANGE ONLINE (PLAN 2)
        eo_consumed = eo_sku['consumedUnits']
        eo_enabled = eo_sku['prepaidUnits']['enabled']
        if eo_enabled - eo_consumed <= threshold:
            send_notification = True

        sec_sku = ms_graph_subscribed_sku("2347355b-4e81-41a4-9c22-55057a399791", token)  # MICROSOFT 365 SECURITY AND COMPLIANCE FOR FLW
        sec_consumed = sec_sku['consumedUnits']
        sec_enabled = sec_sku['prepaidUnits']['enabled']
        if sec_enabled - sec_consumed <= threshold:
            send_notification = True

        subject = f"Notification - Microsoft M365 licence availability has dropped to warning threshold ({threshold})"
        message = f"""This is an automated notification regarding Microsoft 365 licence usage availability. User account licence consumption:\n\n
        Microsoft 365 E5 (On-premise): {e5_consumed} / {e5_enabled}\n\n
        Microsoft 365 F3 (Cloud): {f3_consumed} / {f3_enabled}\n
        Exchange Online (Plan 2): {eo_consumed} / {eo_enabled}\n
        Microsoft 365 Security and Compliance for Firstline Workers: {sec_consumed} / {sec_enabled}\n
        """
        html_message = f"""<p>This is an automated notification regarding Microsoft 365 licence usage availability. User account licence consumption:</p>
        <ul>
        <li>Microsoft 365 E5 (On-premise): {e5_consumed} / {e5_enabled}</li>
        <li>Microsoft 365 F3 (Cloud): {f3_consumed} / {f3_enabled}</li>
        <li>Exchange Online (Plan 2): {eo_consumed} / {eo_enabled}</li>
        <li>Microsoft 365 Security and Compliance for Firstline Workers: {sec_consumed} / {sec_enabled}</li>
        </ul>"""

        if send_notification:
            logger = logging.getLogger('organisation')
            logger.warning(subject)
            mail.send_mail(
                subject=subject,
                message=message,
                from_email=settings.NOREPLY_EMAIL,
                recipient_list=recipients,
                html_message=html_message,
            )