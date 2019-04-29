from authors.apps.authentication.tests.basetests import BaseTest
from authors.apps.authentication.models import User
from rest_framework import status


class TestUserModels(BaseTest):
    """
    A class test for user models.
    Test creation of users
    """

    def test_create_user(self):
        """
        A model test method for creating users
        """
        self.assertIsInstance(self.user, User)

    def test_create_super_user(self):
        """
        A model test method for creating super users
        """
        self.assertTrue(self.super_user.is_staff)


class TestUserSignup(BaseTest):
    """
    A class to test Signup API endpoint.
    Test user signup credentials
    """

    def test_successful_signup(self):
        """
        Test user signup with the correct credentials
        """
        response = self.signup_user("eve", "eve@gmail.com", "@Us3r.com")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', str(response.data))

    def test_signup_without_value(self):
        """
        Test user signup with the missing value credentials
        """
        response = self.signup_user("", "eve@gmail.com", "@Us3r.com")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_with_invalid_value(self):
        """
        Test user signup with invalid value credentials
        """
        response = self.signup_user("evegirl", "evegmail.com", "@Us3r.com")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.signup_user("evegirl", "eve@gmail.com", "@Us")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_with_existing_user(self):
        """
        Test user signup with credentials that exist
        """
        response = self.signup_user("adam", "adam@gmail.com", "@Us3r.com")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_without_key(self):
        """
        Test user signup with the missing keys
        """
        response = self.signup_user_with_missing_key(
            "eve@gmail.com", "@Us3r.com")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestUserLogin(BaseTest):
    """
    A class to test Login API endpoint.
    Test user login credentials
    """

    def test_login_with_correct_credentials(self):
        """
        Test user login with the correct credentials
        """
        response = self.login_user("adam@gmail.com", "@Us3r.com")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', str(response.data))

    def test_login_with_incorrect_credentials(self):
        """
        Test user login with the incorrect credentials
        """
        response = self.login_user("dam@gmail.com", "@Us3r.com")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestUserUpdate(BaseTest):
    """
    A class to test Update API endpoint.
    Test user update credentials
    """

    def test_update_with_user_login(self):
        """
        Test user update with the correct credentials
        """
        self.authenticate_user("adam@gmail.com", "@Us3r.com")
        response = self.update_user("admin1", "adam@gmail.com", "@Us3r.com")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_with_user_logged_out(self):
        """
        Test user update with user not logged in
        """
        response = self.update_user("admin1", "adam@gmail.com", "@Us3r.com")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_with_user_details_exist(self):
        """
        Test user update with user details that exist
        """
        self.authenticate_user("admin@authors.com", "adm123Pass!!")
        response = self.update_user("admin1", "adam@gmail.com", "@Us3r.com")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_with_invalid_value(self):
        """
        Test user update with invalid credentials
        """
        self.authenticate_user("admin@authors.com", "adm123Pass!!")
        response = self.update_user("admin1", "adamgmail.com", "@Us3r.com")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.update_user("evegirl", "eve@gmail.com", "@Us")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestGetUser(BaseTest):
    """
    A class to test Login API endpoint.
    Test user login credentials
    """

    def test_with_logged_in_user(self):
        """
        Test get user with the correct login credentials
        """
        self.authenticate_user("adam@gmail.com", "@Us3r.com")
        response = self.get_user()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_with_logged_out_user(self):
        """
        Test get user without login credentials
        """
        response = self.get_user()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
