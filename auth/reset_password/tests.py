from django.test import TestCase
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from django.core import mail

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
        response = self.client.post(self.url_sendresetpasswordmail, {
            "email": self.user.email
        }, format="json")
        self.assertEqual(response.data['detail'], "Send e-mail succesful")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reset_password_email_no_valid(self):
        response = self.client.post(self.url_sendresetpasswordmail, {
            "email": "worngemailexample.com"
        }, format="json")
        self.assertEqual(response.data['detail'], "No valid email")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_email_not_available(self):
        response = self.client.post(self.url_sendresetpasswordmail, {
            "email": ""
        }, format="json")
        self.assertEqual(response.data['detail'], "No valid email")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_user_not_active(self):
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

    # def test_send_reset_mail_succesfull(self):
    #     response = self.client.post(self.url_sendresetpasswordmail, {
    #         "email": self.user.email
    #     }, format="json")
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data['detail'], "Send e-mail succesful")
    #     self.assertEqual(len(mail.outbox), 1)
    #     self.assertEqual(mail.outbox[0].subject, "You have forgotten your password - Reset your password")



# class ResetPasswordIfLoggedInTestCase(APITestCase):
#     def setUp(self):
#         """
#         Set up a user
#         """
#         self.user = get_user_model().objects.create_user(
#             email="testuser@example.com",
#             password="password"
#         )
#         self.url_resetpasswordmailifloggedin = reverse('resetpasswordmailifloggedin')

#     def test_reset_password_if_login_succesfull(self):
#         response = self.client.post(self.url_resetpasswordmailifloggedin, {
#             "user": self.user,
#             "password_old": self.user.password,
#             "password_new": "newPassword",
#             "password_new_confirm": "newPassword"
#         }, format="json")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['detail'], "Send e-mail succesful")