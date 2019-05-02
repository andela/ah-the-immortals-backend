from .basetests import PasswordResetBaseTest
from rest_framework import status


class TestPasswordReset(PasswordResetBaseTest):
    """
    Tests password reset by user
    """

    def test_invalid_email_address(self):
        """
        Tests posting of invalid email address
        """
        self.reset_data["user"]["email"] = "johnsoon.com"
        response = self.password_reset()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self.contains_error(
                response.data.get("errors").get("email"),
                "Enter a valid email address."
            ), True
        )

    def test_missing_email_field(self):
        """
        tests missing email field
        """
        del self.reset_data["user"]["email"]
        response = self.password_reset()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self.contains_error(
                response.data.get("errors").get("email"),
                "This field is required."
            ), True
        )

    def test_empty_email(self):
        """
        Tests password reset with an empty email
        """
        self.reset_data["user"]["email"] = ""
        response = self.password_reset()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self.contains_error(
                response.data.get("errors").get("email"),
                "This field may not be blank."
            ), True
        )

    def test_null_email(self):
        """
        Tests for input of a null maill
        """
        self.reset_data["user"]["email"] = None
        response = self.password_reset()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self.contains_error(
                response.data.get("errors").get("email"),
                "This field may not be null."
            ), True
        )

    def test_unexisting_ccount(self):
        """
        Tests unexisting account
        """
        self.reset_data["user"]["email"] = "jeff@gmail.com"
        response = self.password_reset()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self.contains_error(
                response.data.get("errors").get("email"),
                "no account with that email address"
            ), True
        )

    def test_unmatching_password(self):
        """
        Tests if passwords match
        """
        self.password_data["password_confirm"] = "SomeTestPassword#!2"
        self.password_reset()
        response = self.password_reset_confirm()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self.contains_error(
                response.data.get("errors").get("password"),
                "passwords did not match"
            ), True
        )

    def test_invalid_password(self):
        """
        Tests invalid password
        """
        self.password_data["password"] = "123"
        self.password_data["password_confirm"] = "123"
        self.password_reset()
        response = self.password_reset_confirm()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self.contains_error(
                response.data.get("errors").get("password"),
                "This password is too short. It must contain at least 8 characters."
            ), True
        )

    def test_invalid_token(self):
        """
        Tests changing of password with invalid token
        """
        self.password_data["token"] = "abcd898adwhi3454asddwhfwh"
        response = self.password_reset_confirm()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self.contains_error(
                response.data.get("errors").get("token"),
                "invalid token"
            ), True
        )

    def test_null_token(self):
        """
        Tests password reset without a null token
        """
        response = self.password_reset_confirm()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self.contains_error(
                response.data.get("errors").get("token"),
                "This field may not be null."
            ), True
        )

    def test_blank_token(self):
        """
        Tests a blank token
        """
        self.password_data["token"] = ""
        response = self.password_reset_confirm()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self.contains_error(
                response.data.get("errors").get("token"),
                "This field may not be blank."
            ), True
        )

    def test_missing_token_field(self):
        """
        Tests missing token field
        """
        del self.password_data["token"]
        response = self.password_reset_confirm()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self.contains_error(
                response.data.get("errors").get("token"),
                "This field is required."
            ), True
        )

    def test_null_password(self):
        """
        Tests a password that is null
        """
        self.password_data["password"] = None
        self.password_reset()
        response = self.password_reset_confirm()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self.contains_error(
                response.data.get("errors").get("password"),
                "This field may not be null."
            ), True
        )

    def test_blank_password(self):
        """
        Tests a password that is blank
        """
        self.password_data["password"] = ""
        self.password_reset()
        response = self.password_reset_confirm()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self.contains_error(
                response.data.get("errors").get("password"),
                "This field may not be blank."
            ), True
        )

    def test_missing_password_field(self):
        """
        Tests missing password field
        """
        del self.password_data["password"]
        response = self.password_reset_confirm()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self.contains_error(
                response.data.get("errors").get("password"),
                "This field is required."
            ), True
        )

    def test_blank_password_confirm(self):
        """
        Tests blank password confirm
        """
        self.password_data["password_confirm"] = ""
        self.password_reset()
        response = self.password_reset_confirm()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self.contains_error(
                response.data.get("errors").get("password_confirm"),
                "This field may not be blank."
            ), True
        )

    def test_null_password_confirm(self):
        """
        Tests null password confirm
        """
        self.password_data["password_confirm"] = None
        self.password_reset()
        response = self.password_reset_confirm()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self.contains_error(
                response.data.get("errors").get("password_confirm"),
                "This field may not be null."
            ), True
        )

    def test_missing_password_confirm_field(self):
        """
        Tests missing password field
        """
        del self.password_data["password_confirm"]
        response = self.password_reset_confirm()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self.contains_error(
                response.data.get("errors").get("password_confirm"),
                "This field is required."
            ), True
        )

    def test_successful_password_reset(self):
        """
        Tests successful password rese
        """
        self.password_reset()
        response = self.password_reset_confirm()
        message = None
        for item in response.data.get("data"):
            if item.get("message"):
                message = item.get("message")
                break
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            message,
            "you have successfully reset your password"
        )

    def test_token_reuse(self):
        """
        Tests if a user can use token generated more than once to
        reset password
        """
        self.password_reset()
        self.password_reset_confirm()
        response = self.password_reset_confirm()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self.contains_error(
                response.data.get("errors").get("token"),
                "invalid token"
            ), True
        )
