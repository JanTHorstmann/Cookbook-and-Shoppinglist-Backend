from django.test import TestCase
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from django.core import mail
import re
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from urllib.parse import urlparse
from django.core.exceptions import ValidationError
from .utils import extract_link_uid_and_token_from_email

User = get_user_model()
class SendResetPasswordMailTestCase(APITestCase):

    def setUp(self):
        """
        Set up a user
        """
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com",
            password="password",
            is_active=True
        )
        # self.url_resetpasswords = reverse('resetpasswords')
        self.url_sendresetpasswordmail = reverse('sendresetpasswordmail')
        # self.url_resetpasswordmailifloggedin = reverse('resetpasswordmailifloggedin')


    def test_reset_password_email_valid(self):
        """
        Sends a POST request with the valid user's email.
        Asserts that the response has status 200 and the success message is returned.
        """
        response = self.client.post(self.url_sendresetpasswordmail, {
            "email": self.user.email
        }, format="json")
        self.assertEqual(response.data['detail'], "Send e-mail succesful")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_reset_password_email_no_valid(self):
        """
        Sends a POST request with an invalid email format.
        Asserts that a 400 Bad Request status and the expected error message are returned.
        """
        response = self.client.post(self.url_sendresetpasswordmail, {
            "email": "worngemailexample.com"
        }, format="json")
        self.assertEqual(response.data['detail'], "No valid email")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_reset_password_email_not_available(self):
        """
        Sends a POST request with an empty email field.
        Asserts that a 400 Bad Request and error message are returned.
        """
        response = self.client.post(self.url_sendresetpasswordmail, {
            "email": ""
        }, format="json")
        self.assertEqual(response.data['detail'], "No valid email")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_reset_password_user_not_active(self):
        """
        Creates a new inactive user, then tries to send a reset password mail.
        Asserts that a 200 OK is returned and a message indicating account confirmation is required.
        """        
        self.user = get_user_model().objects.create_user(
            email="not_active_test_user@example.com",
            password="password",
            is_active=False
        )
        response = self.client.post(self.url_sendresetpasswordmail, {
            "email": "not_active_test_user@example.com"
        }, format="json")
        self.assertEqual(response.data['detail'], "Account is not yet confirmed - confirmation email sent again")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_email_is_sends(self):
        """
        Sends a reset password email to the test user.
        Asserts that:
        - the request is successful (200),
        - exactly one email was sent,
        - and the subject matches the expected reset email subject.
        """
        response = self.client.post(self.url_sendresetpasswordmail, {
                "email": self.user.email
            }, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'You have forgotten your password - Reset your password')   
        
        
class SendRestPasswordLinkTokenUIDTestCase(APITestCase):

    def setUp(self):
        """
        Set up a user
        """
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com",
            password="password",
            is_active=True
        )
        self.url_sendresetpasswordmail = reverse('sendresetpasswordmail')


    def test_email_contains_reset_link_with_token_and_uid(self):
        """
        Sends the reset email, extracts the link from the email body using regex.
        Asserts that:
        - a URL exists in the email,
        - the URL contains both a valid uidb64 and a token.
        """
        response = self.client.post(self.url_sendresetpasswordmail, {
            "email": self.user.email
        }, format="json")

        email_body = mail.outbox[0].body
        match_link = re.search(r'https?://[^\s]+', email_body)
        reset_link = match_link.group(0)
        match = re.search(r'/forget-password-reset/(?P<uidb64>[^/]+)/(?P<token>[^/]+)/', reset_link)

        self.assertIsNotNone(match, "No URL found in email body")
        self.assertIsNotNone(match, "Reset URL does not contain UID and token")
        

    def test_email_contains_token(self):
        """
        Sends the reset email, extracts the token via helper function.
        Asserts that the token is valid for the given user by using Django’s default_token_generator.
        """
        response = self.client.post(self.url_sendresetpasswordmail, {
            "email": self.user.email
        }, format="json")

        link, uidb64, token = extract_link_uid_and_token_from_email(self)
        self.assertTrue(default_token_generator.check_token(self.user, token))


    def test_email_contains_uid(self):
        """
        Sends the reset email, extracts the UID via helper.
        Decodes the uidb64 and asserts it matches the user's actual ID.
        """
        response = self.client.post(self.url_sendresetpasswordmail, {
            "email": self.user.email
        }, format="json")

        link, uidb64, token = extract_link_uid_and_token_from_email(self)
        uid = urlsafe_base64_decode(uidb64).decode()
        self.assertEqual(int(uid), self.user.id)
            

class ConfirmResetPasswordTestCase(APITestCase):

    def setUp(self):
        """
        Set up a user and send a reset password email to obtain a valid UID and token.
        """
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com",
            password="password",
            is_active=True
        )
        # self.url_resetpasswords = reverse('resetpasswords')
        self.url_sendresetpasswordmail = reverse('sendresetpasswordmail')
        
        response = self.client.post(self.url_sendresetpasswordmail, {
            "email": self.user.email
        }, format="json")

        link, uidb64, token = extract_link_uid_and_token_from_email(self)
        self.link = link
        self.uidb64 = uidb64
        self.token = token


    def test_change_password_successful(self):
        """
        Valid password reset should succeed and update the password.
        """
        new_password = "NewStrongPassword123#"
        parsed_path = urlparse(self.link).path.replace("/forget-password-reset/", "/api/resetpasswords/")
        response = self.client.post(parsed_path, {
            "password": new_password,
            "password_confirm": new_password
        }, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["detail"], "Password reset successful")
        
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))
        self.assertFalse(self.user.check_password("password"))  


    def test_new_passwords_do_not_match(self):
        """
        Passwords that don't match should result in an error.
        """
        parsed_path = urlparse(self.link).path.replace("/forget-password-reset/", "/api/resetpasswords/")
        response = self.client.post(parsed_path, {
            "password": "NewStrongPassword123#",
            "password_confirm": "NewStrongPassword123*"
        }, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Passwords do not match.", str(response.data))


    def test_new_password_does_not_meet_minimum_requirements(self):
        """
        Passwords that are too short should trigger validation errors.
        """
        parsed_path = urlparse(self.link).path.replace("/forget-password-reset/", "/api/resetpasswords/")
        response = self.client.post(parsed_path, {
            "password": "123456",
            "password_confirm": "123456"
        }, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("This password is too short. It must contain at least 8 characters.", str(response.data))

    
    def test_token_can_only_be_used_once(self):
        """
        The reset token should become invalid after it is used once.
        """
        new_password = "NewStrongPassword123#"
        parsed_path = urlparse(self.link).path.replace("/forget-password-reset/", "/api/resetpasswords/")
        response = self.client.post(parsed_path, {
            "password": new_password,
            "password_confirm": new_password
        }, format="json")

        response = self.client.post(parsed_path, {
            "password": new_password,
            "password_confirm": new_password
        }, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["detail"], "Invalid or expired token")

    def test_invalid_or_expired_token(self):
        """
        Using an invalid or expired token should return an error.
        """
        new_password = "NewStrongPassword123#"
        parsed_path = urlparse(self.link).path.replace("/forget-password-reset/", "/api/resetpasswords/")
        invalid_path = parsed_path.replace(self.token, "invalid_token")
        response = self.client.post(invalid_path , {
            "password": new_password,
            "password_confirm": new_password
        }, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["detail"], "Invalid or expired token")


    def test_invalid_uid(self):
        """
        Using a malformed UID should result in an invalid link error.
        """
        parsed_path = urlparse(self.link).path.replace("/forget-password-reset/", "/api/resetpasswords/")
        invalid_path = parsed_path.replace(self.uidb64, "invalid_uid")

        response = self.client.post(invalid_path, {
            "password": "AnotherNewPassword123#",
            "password_confirm": "AnotherNewPassword123#"
        }, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["detail"], "Invalid link")