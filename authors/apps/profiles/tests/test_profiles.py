from rest_framework import status

from authors.apps.profiles.tests.basetests import BaseTest


class TestViewProfile(BaseTest):
    """
    Tests for viewing profile
    """

    def test_successfully_getting_profile(self):
        """
        Test view profile successfully
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        response = self.get_profile_with_valid_username()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("profile").get("username"), "adam")

    def test_getting_profile_with_invalid_username(self):
        """
        Test view profile for invalid username
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        response = self.get_profile_with_invalid_username()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("error"), "User does not exist")

    def test_update_profile_successfuly(self):
        """
        Test method for successfully updtaing a user
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        response = self.update_user_profile("Abraham", "Kamau", "I love history")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("profile").get("last_name"), "Kamau")

    def test_update_profile_while_loggedout(self):
        """
        Test method for updating while user is not authenticated
        """
        response = self.update_user_profile(
            "Abraham", "Kamau", "I love history")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("detail"), "Authentication credentials were not provided.")

    def test_update_profile_while_not_owner(self):
        """
        Test method for updating while user is not owner
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        response = self.update_another_user_profile(
            "Abraham", "Kamau", "I love history")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("error"), "You do not own this profile")
    
    def test_update_profile_while_not_exist(self):
        """
        Test method for updating while user is not owner
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        response = self.update_user_profile_notexist(
            "Abraham", "Kamau", "I love history")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("error"), "User does not exist")

    def test_successfully_listing_profiles(self):
        """
        Test listing of user profiles 
        """
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        response = self.list_profiles()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data.get("profiles")[0], dict)

    def test_listing_profiles_with_unauthorised_user(self):
        """
        Test listing of user profiles with unauthorised user
        """
        response = self.list_profiles()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get("detail"),
                         "Authentication credentials were not provided.")