# -*- coding:utf-8 -*-
from time import sleep

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Send emails to all activated users."

    def handle(self, *args, **options):
        from services.email import send_email

        i = 0
        with open('/home/serg/emails.txt') as f:
            emails = [line.strip() for line in f]
            i += 1
            if i > 9000:
                break

        for email in emails:
            print email
            send_email(None, u'Гракон готовится к выборам 14 октября',
                    'letters/invitation.html', {}, '14_10_invitation', 'noreply', to_email=email)
            sleep(0.2)
