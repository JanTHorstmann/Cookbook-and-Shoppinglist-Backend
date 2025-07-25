from django.test import TestCase
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from django.core import mail
import re
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode

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

        uidb64, token = self.extract_uid_and_token_from_email()
        self.assertTrue(default_token_generator.check_token(self.user, token))


    def test_email_contains_uid(self):
        """
        Sends the reset email, extracts the UID via helper.
        Decodes the uidb64 and asserts it matches the user's actual ID.
        """
        response = self.client.post(self.url_sendresetpasswordmail, {
            "email": self.user.email
        }, format="json")

        uidb64, _ = self.extract_uid_and_token_from_email()
        uid = urlsafe_base64_decode(uidb64).decode()
        self.assertEqual(int(uid), self.user.id)


    def extract_uid_and_token_from_email(self):
        """
        Helper method to extract the uidb64 and token from the reset link inside the email.
        Returns a tuple: (uidb64, token).
        Asserts that:
        - one email was sent,        
        - the email contains a URL,
        - the URL matches the pattern /forget-password-reset/<uidb64>/<token>/.
        """
        self.assertEqual(len(mail.outbox), 1, "No email was sent")
        email_body = mail.outbox[0].body

        match_link = re.search(r'https?://[^\s]+', email_body)
        self.assertIsNotNone(match_link, "No URL found in email body")
        reset_link = match_link.group(0)

        match = re.search(r'/forget-password-reset/(?P<uidb64>[^/]+)/(?P<token>[^/]+)/', reset_link)
        self.assertIsNotNone(match, "Reset URL does not contain UID and token")

        return match.group("uidb64"), match.group("token")