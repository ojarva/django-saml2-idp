"""
Tests for basic view functionality only.
"""
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client


class TestLoginView(TestCase):
    pass


class TestLoginProcessView(TestCase):
    pass


class TestLogoutView(TestCase):
    def test_logout(self):
        """
        Response did not say logged out.
        """
        response = self.client.get('/idp/logout/')
        self.assertContains(response, 'logged out', status_code=200)

    def test_logout_user(self):
        """
        User account not logged out.
        """
        fred = User.objects.create_user('fred', email='fred@example.com', password='secret')
        self.client.login(username='fred', password='secret')
        self.assertTrue('_auth_user_id' in self.client.session, 'Did not login test user; test is broken.')
        response = self.client.get('/idp/logout/')
        self.assertTrue('_auth_user_id' not in self.client.session, 'Did not logout test user.')
