# -*- coding: UTF-8 -*-

from django.test import TestCase
from django.core import mail
from django.test.client import Client
from django.contrib.auth.models import User
from models import *

def data():
    '''
    Data for testing include 2 Users: admin and juanjo,
    3 Notice Types: Error, Warning and Information,
    5 Notices:
        Archived notice
        Notice to juanjo
        Notice to admin 3
        Notice to admin 2
        Notice to admin 1
    '''
    return ['users.json', 'notice_types.json', 'notices.json']

class TestNotice(TestCase):    
    fixtures = data()
    def setUp(self):
        self.admin = User.objects.create(username='admin', email="admin@example.com")
        self.juanjo = User.objects.create(username='juanjo', email="juanjo@example.com")
        self.error = create_notice_type('Error', 'error', 'ERROR[%(added)s]: %(messages)s', EMAIL_MEDIUM)
        self.warning = create_notice_type('Warning', 'digested warnings', 'here is a collection of recent warnings.', DIGEST_MEDIUM)
        self.info = create_notice_type('Info', 'important information', '', SCREEN_MEDIUM)
        self.n1 = send ([self.admin], 'Error', {'message': 'n1 error'}, now=True)[0]
        self.assertEquals(self.n1.__class__,Notice)
                
    def test_notices(self):
        send ([self.admin], 'Error', {'message': 'a red light in on'}, now=True)
        self.assertEquals(len(mail.outbox), 2)
        send ([self.admin], 'Warning', {'message': 'a yellow light is on'}, now=True)
        self.assertEquals(len(mail.outbox), 2)
        send ([self.juanjo], 'Info', {'message': 'the world is round'}, now=True)
        self.assertEquals(len(mail.outbox), 2)
        self.n1.archive()
        self.assertEquals(len(Notice.objects.notices_for(self.admin)), 2)
        self.assertEquals(len(Notice.objects.notices_for(self.admin, archived=True)), 3)
        self.assertEquals(len(Notice.objects.notices_for(self.juanjo)), 1)
