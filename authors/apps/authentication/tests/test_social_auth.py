from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status

from unittest import mock

from .basetests import BaseTest


class TestSocialLogin(BaseTest):
    """
    Class to test Social Login
    """

    def setUp(self):
        """
        Set up test environment
        """
        self.path = "authors.apps.authentication.views.SocialAuthAPIView.create"
        self.social_url = reverse("authentication:social")
        self.facebook_user = {
            "provider": "facebook",
            "access_token": "96930231-8iCEKaIwsSlQCSpHhFWD7WOJj5KXAN9CZFUkT"
        }

        self.google_user = {
            "provider": "google-oauth2",
            "access_token": "96930231-8iCEKaIwsSlQCSpHhFWD7WOJj5KXAN9CZFUkTK"
        }

        self.twitter_user = {
            "provider": "twitter",
            "access_token": "96930231-NeiGSUbnIrSjjEQY7LPmZc7Ge7J7FPXIzrHjTLMT4",
            "access_token_secret": "bUBaLmy4Gf5DdNluet1qAIm4z26lF98pFsdKGiBvsLlnh"
        }

        self.invalid_token = {
            "provider": "twitter",
            "access_token": "96930231-8iCEKaIwsSlQCSpHhFWD7WOJj5KXAN9CZFUkT",
            "access_token_secret": "wVJOR7RlsXVAS04QBHlGfPsWz4REHcvhUutDQQoD"
        }

        self.unsupported_user = {
            "provider": "amazon",
            "access_token": "96930231-8iCEKaIwsSlQCSpHhFWD7WOJj5KXAN9CZFUkTK"
        }

        self.social_response = {
                "email": "james@gmail.com",
                "username": "mathenge"
                }

        self.missing_backend = {
                "error": "Provider invalid or not supported"
                }

    def test_successful_login_with_google(self):
        """
        Test successful login with google
        """
        with mock.patch(self.path) as mocked_google_auth:
            mocked_google_auth.return_value = Response(self.social_response, status=status.HTTP_200_OK)
            res = self.social_login(self.social_url, self.google_user)
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertEqual(res.data.get('email'), "james@gmail.com")

    def test_successful_login_with_twitter(self):
        """
        Test successful login with twitter
        """
        with mock.patch(self.path) as mocked_twitter_auth:
            mocked_twitter_auth.return_value = Response(self.social_response, status=status.HTTP_200_OK)
            res = self.social_login(self.social_url, self.twitter_user)
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertEqual(res.data.get('email'), "james@gmail.com")

    def test_successful_login_with_facebook(self):
        """
        Test successful login with facebook
        """
        with mock.patch(self.path) as mocked_facebook_auth:
            mocked_facebook_auth.return_value = Response(self.social_response, status=status.HTTP_200_OK)
            res = self.social_login(self.social_url, self.facebook_user)
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertEqual(res.data.get('username'), "mathenge")

    def test_missing_backend(self):
        """
        Test unsupported social provider
        """
        res = self.social_login(self.social_url, self.unsupported_user)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(res.data.get('error'), "Provider invalid or not supported")

    def test_valid_access_token(self):
        """
        Test valid access token login
        """
        res = self.social_login(self.social_url, self.twitter_user)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get('username'), "matthenge")

    def test_invalid_access_token(self):
        """
        Test invalid access token
        """
        res = self.social_login(self.social_url, self.google_user)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data.get('error'), "Invalid credentials")

    def test_invalid_access_token_secret(self):
        """
        Test invalid access token secret for twitter
        """
        res = self.social_login(self.social_url, self.invalid_token)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data.get('error'), "Invalid credentials")
