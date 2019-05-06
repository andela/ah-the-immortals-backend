from authors.apps.authentication.tests.basetests import BaseTest
from authors.apps.authentication.models import User
from rest_framework import status


class TestValidations(BaseTest):
    """Test suite for validations."""

    def test_invalid_username(self):
        """
        Test user signup with invalid username
        """
        response = self.signup_user("@@ @@", "test@gmail.com", "12qQqetfdt")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        errors = response.data['errors']
        self.assertEqual(
            errors['username'][0], "Username can only contain letters, numbers, underscores, and hyphens")

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
            errors['email'][0], "Enter a valid email address.")

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
        response = self.signup_user("test", "test@gmail.com", "R31w@")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        errors = response.data['errors']
        self.assertEqual(errors['password'][0],
                         "password should have at least 2 uppercase letters")
        self.assertEqual(
            errors['password'][1], "password should have at least 3 lowercase letters")

    def test_non_alphanumeric_password(self):
        """
        Test user signup with the special characters as password
        """
        response = self.signup_user("test", "test@gmail.com", "@@@@@@@@@@")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        errors = response.data['errors']
        self.assertEqual(
            errors['password'][0], "password should have at least 2 uppercase letters")
        self.assertEqual(
            errors['password'][1], "password should have at least 3 lowercase letters")
        self.assertEqual(
            errors['password'][2], "password should have at least 2 digits")
        self.assertEqual(
            errors['password'][3], "password should not have a repeating characters")

    def test_password_with_no_special_character(self):
        """
        Test user signup with a password with no special character
        """
        response = self.signup_user("test", "test@gmail.com", "12WEerrhfj")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        errors = response.data['errors']
        self.assertEqual(
            errors['password'][0], "password should have at least 1 special character")

    def test_password_with_repeating_character(self):
        """
        Test user signup with repeating characters on a password
        """
        response = self.signup_user("test", "test@gmail.com", "12WEerr@rrhfj")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        errors = response.data['errors']
        self.assertEqual(
            errors['password'][0], "password should not have a repeating characters")

    def test_password_with_repeating_sequence(self):
        """
        Test user signup with repeating sequence on a password
        """
        response = self.signup_user("test", "test@gmail.com", "1234W@rhTTfj")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        errors = response.data['errors']
        self.assertEqual(
            errors['password'][0], "password should not have a repeating sequence")
