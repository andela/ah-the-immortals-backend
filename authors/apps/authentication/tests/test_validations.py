from authors.apps.authentication.tests.basetests import BaseTest
from authors.apps.authentication.models import User
from rest_framework import status


class TestValidations(BaseTest):
    """Test suite for validations."""

    def test_invalid_username(self):
        """
        Test user signup with invalid username
        """
        response = self.signup_user("@@@@", "test@gmail.com", "12qQqetfdt")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        errors = response.data['errors']
        self.assertEqual(
            errors['username'][0], "Username should be at least 3 characters, have no spaces or special characters except hyphen-, fullstop. and underscore_")

    def test_empty_username(self):
        """
        Test user signup with invalid username
        """
        response = self.signup_user_with_missing_key(
            "test@gmail.com", "12qQqetfdt")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        errors = response.data['errors']
        self.assertEqual(errors['username'][0], "Username is a required field")

    def test_existing_username(self):
        """
        Test user signup with existing username
        """
        response = self.signup_user("adam", "test@gmail.com", "12qQqetfdt")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        errors = response.data['errors']
        self.assertEqual(errors['username'][0],
                         "user with this username already exists")

    def test_invalid_email(self):
        """
        Test user signup with invalid email address
        """
        response = self.signup_user("test", "testgmail.com", "12qQqetfdt")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        errors = response.data['errors']
        self.assertEqual(
            errors['email'][0], "Email must be of the format name@domain.com")

    def test_existing_email(self):
        """
        Test user signup with existing email
        """
        response = self.signup_user("elly", "adam@gmail.com", "12qQqetfdt")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        errors = response.data['errors']
        self.assertEqual(errors["email"][0],
                         "user with this email already exists")

    def test_short_password(self):
        """
        Test user signup with the short password
        """
        response = self.signup_user("test", "test@gmail.com", "1234")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        errors = response.data['errors']
        self.assertEqual(errors['password'][0],
                         "Password must be at least 8 characters long")
        self.assertEqual(
            errors['password'][1], "Password must have three lowercase, two upercase, one special case letters and two digits eg 12aaaAA@")
