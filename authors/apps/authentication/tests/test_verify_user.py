from authors.apps.authentication.tests.basetests import BaseTest
from rest_framework import status


class TestUserVerification(BaseTest):
    """
    This class handles the testing of User Verification
    """

    def test_successfull_verification(self):
        token = self.generate_jwt_token('pablo@escobar.com', 'Escobar')
        url = self.verification_of_user + token

        response = self.client.get(url)
        self.assertEqual(response.data['message'],
                         "You have been verified successfully")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_verification_token(self):
        self.signup_user('Elchapo', 'el@chapo.com', 'Maina9176')
        self.verify_user('el@chapo.com')
        token = self.generate_jwt_token('el@chapo.com', 'Elchapo')
        url = self.verification_of_user + token

        response = self.client.get(url)

        self.assertEqual(response.data['message'],
                         "Your email is already verified")
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_invalid_verification_token(self):
        token = "sidvfldifhsv"
        url = self.verification_of_user + token

        response = self.client.get(url)
        self.assertEqual(
            response.data['detail'], "Invalid Token. The token provided cannot be decoded!")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_expired_jwt_token(self):
        token = self.generate_expired_token()
        url = self.verification_of_user + token

        response = self.client.get(url)
        self.assertEqual(
            response.data['detail'],
            'The token used has expired. Please authenticate again!')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
