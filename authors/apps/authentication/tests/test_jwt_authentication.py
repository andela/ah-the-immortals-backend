from authors.apps.authentication.tests.basetests import BaseTest
from rest_framework import status


class TestTokenAuthentication(BaseTest):
    """
    This class handles the testing of JWTAuthentication
    """

    def test_get_jwt_with_unverified_user_after_login(self):
        self.signup_user('Pablo', 'pablo@escobar.com', 'TheMerin123')
        response = self.login_user('pablo@escobar.com', 'TheMerin123')
        self.assertIn('error', str(response.data))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_jwt_after_login(self):
        self.signup_user('issa', 'issamwangi@gmail.com', '@Us3r.co3mW')
        self.verify_user('issamwangi@gmail.com')
        response = self.login_user('issamwangi@gmail.com', '@Us3r.co3mW')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_jwt_after_signup(self):
        response = self.signup_user(
            'issa', 'issamwangi@gmail.com', '@Us3r.co3mW')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invalid_authorization_header(self):
        token = self.generate_jwt_token('issamwangi@gmail.com', 'issa')
        self.client.credentials(
            HTTP_AUTHORIZATION=token)
        response = self.client.get(self.get_url)
        self.assertEqual(
            response.data['detail'],
            'The authorization header provided is invalid!')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_header_prefix(self):
        token = self.generate_jwt_token('issamwangi@gmail.com', 'issa')
        self.client.credentials(
            HTTP_AUTHORIZATION='Invalid ' + token)
        response = self.client.get(self.get_url)
        self.assertEqual(
            response.data['detail'],
            'Please use a Bearer token!')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_token(self):
        token = 'sxdcfvgbhjklrty567dfg'
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.get(self.get_url)
        self.assertEqual(
            response.data['detail'],
            'Invalid Token. The token provided cannot be decoded!')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_inactive_user(self):
        token = self.generate_jwt_token('ian@gmail.com', 'ian')
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.get(self.get_url)
        self.assertEqual(
            response.data['detail'],
            'Your account is not active!')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_not_found_from_token(self):
        token = self.generate_jwt_token('ianmwangi@gmail.com', 'ianmaina')
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.get(self.get_url)
        self.assertEqual(
            response.data['detail'],
            'No user was found from the provided token!')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_expired_jwt_token(self):
        token = self.generate_expired_token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.get(self.get_url)
        self.assertEqual(
            response.data['detail'],
            'The token used has expired. Please authenticate again!')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
