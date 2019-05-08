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
        self.reset_data["email"] = "johnsoon.com"
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
        del self.reset_data["email"]
        response = self.password_reset()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self.contains_error(
                response.data.get("errors").get("email"),
                "Please provide your email address"
            ), True
        )

    def test_empty_email(self):
        """
        Tests password reset with an empty email
        """
        self.reset_data["email"] = ""
        response = self.password_reset()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self.contains_error(
                response.data.get("errors").get("email"),
                "Please provide your email address"
            ), True
        )

    def test_null_email(self):
        """
        Tests for input of a null maill
        """
        self.reset_data["email"] = None
        response = self.password_reset()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self.contains_error(
                response.data.get("errors").get("email"),
                "Please provide your email address"
            ), True
        )

    def test_successful_reset_link_sent(self):
        """
        Tests for successful sending of the password
        reset link
        """
        response = self.password_reset()
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            response.data.get("data")[0].get("message"),
            "A password reset message was sent to your email address. Please click the link in that message to reset your password"
        )

    def test_unexisting_ccount(self):
        """
        Tests unexisting account
        """
        self.reset_data["email"] = "jeff@gmail.com"
        response = self.password_reset()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self.contains_error(
                response.data.get("errors").get("email"),
                "No account with that email address"
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
                "Passwords did not match"
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
        self.generate_fake_token()
        response = self.password_reset_confirm()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self.contains_error(
                response.data.get("errors").get("token"),
                "Invalid token"
            ), True
        )

    def test_null_token(self):
        """
        Tests for null token
        """
        response = self.password_reset_confirm()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self.contains_error(
                response.data.get("errors").get("token"),
                "There is no token provided"
            ), True
        )

    def test_expired_token(self):
        self.generate_expired_token()
        response = self.password_reset_confirm()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self.contains_error(
                response.data.get("errors").get("token"),
                "Expired token"
            ), True
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
                "Invalid token"
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
                "Please provide your password"
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
                "Please provide your password"
            ), True
        )

    def test_missing_password(self):
        """
        Tests missing password field
        """
        del self.password_data["password"]
        self.password_reset()
        response = self.password_reset_confirm()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self.contains_error(
                response.data.get("errors").get("password"),
                "Please provide your password"
            ), True
        )

    def test_less_than_2_uppercase_in_password(self):
        """
        Tests a password that has less than two uppercase letters
        """
        self.password_data["password"] = "Henkdestpass23!#"
        self.password_data["password_confirm"] = "Henkdestpass23!#"
        self.password_reset()
        response = self.password_reset_confirm()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self.contains_error(
                response.data.get("errors").get("password"),
                "Your password should have a minimum of 2 uppercase letters"
            ), True
        )

    def test_less_than_2_numbers_in_password(self):
        """
        Tests for a password that has less than two integers from {0...9}
        """
        self.password_data["password"] = "HenkDTestPAss2!#"
        self.password_data["password_confirm"] = "HenkDTestPAss2!#"
        self.password_reset()
        response = self.password_reset_confirm()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self.contains_error(
                response.data.get("errors").get("password"),
                "Your password should have a minimum of 2  numbers"
            ), True
        )

    def test_special_character_in_password(self):
        """
        Tests for a password that has no special character
        """
        self.password_data["password"] = "HenkDTestPAss23"
        self.password_data["password_confirm"] = "HenkDTestPAss23"
        self.password_reset()
        response = self.password_reset_confirm()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self.contains_error(
                response.data.get("errors").get("password"),
                "Your password should have a minimum of 1 special character"
            ), True
        )

    def test_less_than_3_lowercase_in_password(self):
        """
        Tests for password with less than three lowercase letters
        """
        self.password_data["password"] = "HENKKDTAKPAab23!#"
        self.password_data["password_confirm"] = "HENKKDTAKPAab23!#"
        self.password_reset()
        response = self.password_reset_confirm()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self.contains_error(
                response.data.get("errors").get("password"),
                "Your password should have a minimum of 3 lowercase letters"
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
                "Please confirm your password"
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
                "Please confirm your password"
            ), True
        )

    def test_missing_password_confirm(self):
        """
        Tests missing password field
        """
        del self.password_data["password_confirm"]
        self.password_reset()
        response = self.password_reset_confirm()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self.contains_error(
                response.data.get("errors").get("password_confirm"),
                "Please confirm your password"
            ), True
        )

    def test_missing_password_and_password_confirm(self):
        """
        Tests when a password and a confirmation password is missing
        """
        del self.password_data["password"]
        del self.password_data["password_confirm"]
        self.password_reset()
        response = self.password_reset_confirm()
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(
            self.contains_error(
                response.data.get("errors").get("password"),
                "Please provide your password"
            ), True
        )
        self.assertEqual(
            self.contains_error(
                response.data.get("errors").get("password_confirm"),
                "Please confirm your password"
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
            "You have successfully reset your password"
        )
