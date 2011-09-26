"""
Tests for basic view functionality only.
"""
from django.test import TestCase
from django.test.client import Client


class TestLoginView(TestCase):
    pass


class TestLoginProcessView(TestCase):
    pass


class TestLogoutView(TestCase):
    def test_logout(self):
        response = self.client.get('/idp/logout/')
        self.assertContains(response, 'logged out', status_code=200)
