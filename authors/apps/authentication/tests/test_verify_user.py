from authors.apps.authentication.tests.basetests import BaseTest
from rest_framework import status


class TestUserVerification(BaseTest):
    """
    This class handles the testing of User Verification
    """

    def setUp(self):
        super().setUp()
        self.user.is_verified = False
        self.user.save()

    def verify(self, token):
        """
        Verifies a user
        """
        url = self.verification_of_user + token
        response = self.client.get(url)
        return response

    def test_successfull_verification(self):
        token = self.generate_auth_token().key
        response = self.verify(token)
        self.assertEqual(response.data['message'],
                         "You have been verified successfully")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_used_verification_token(self):
        token = self.generate_auth_token().key
        self.verify(token)
        response = self.verify(token)
        self.assertEqual(response.data['message'],
                         "Your email is already verified")
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_invalid_verification_token(self):
        token = self.generate_fake_auth_token()
        response = self.verify(token)
        self.assertEqual(
            response.data['detail'], "Invalid Token. The token provided cannot be decoded!")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_expired_auth_token(self):
        token = self.generate_expired_auth_token().key
        response = self.verify(token)
        self.assertEqual(
            response.data['detail'],
            'The token used has expired. Please authenticate again!')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
