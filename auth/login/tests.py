from django.test import TestCase
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from django.urls import reverse
from django.core import mail
from axes.models import AccessAttempt
from axes.handlers.proxy import AxesProxyHandler

User = get_user_model()

class BaseLoginTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.login_url = reverse('login')
        cls.email = "testuser@example.com"
        cls.password = "SecurePassword123"
        cls.user = User.objects.create_user(email=cls.email, password=cls.password, is_active=True)

class BaseBruteForceLoginTestCase(BaseLoginTestCase):
    def setUp(self):
        for _ in range(10):
            response = self.client.post(self.login_url, {
                "email": self.email,
                "password": "wrongPassword"
            }, format="json")
    
class LoginTestCase(BaseLoginTestCase):

    def test_successful_login(self):
        response = self.client.post(self.login_url, {
            "email": self.email,
            "password": self.password
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIsInstance(response.data["access"], str)
        self.assertIsInstance(response.data["refresh"], str)

    def test_login_user_is_active_false(self):
        self.user.is_active = False
        self.user.save()
        response = self.client.post(self.login_url, {
            "email": self.email,
            "password": self.password
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Email is not confirmed")

    def test_login_with_false_email(self):
        response = self.client.post(self.login_url, {
            "email": "falseEmail@example.com",
            "password": self.password
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "E-mail or password is incorrect")

    def test_login_with_false_password(self):
        response = self.client.post(self.login_url, {
            "email": self.email,
            "password": "wrongPassword"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "E-mail or password is incorrect")

    def test_no_email_before_limit(self):
        for _ in range(9):
            self.client.post(self.login_url, {
                "email": self.email,
                "password": "wrongPassword"
            }, format="json")
        
        self.assertEqual(len(mail.outbox), 0)



class BruteForceLoginTestCase(BaseBruteForceLoginTestCase):

    def test_brute_force_lockout(self):
        response = self.client.post(self.login_url, {
                "email": self.email,
                "password": "wrongPassword"
            }, format="json")
        
        user = User.objects.get(email=self.email)
        self.assertTrue(user.lockout_email_sent)
        self.assertEqual(response.data["detail"], "Too many failed login attempts. Please check your emails")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_brute_force_triggers_email(self):
        response = self.client.post(self.login_url, {
                "email": self.email,
                "password": "wrongPassword"
            }, format="json")
        
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Too many login attempts - Reset your password')

    def test_only_one_email_sent_on_lockout(self):
        for _ in range(2):
            self.client.post(self.login_url, {
                "email": self.email,
                "password": "wrongPassword"
            }, format="json")

        self.assertEqual(len(mail.outbox), 1)

    def test_other_user_not_locked_out_with_same_ip(self):
        # simulate brute-force attack from 1.2.3.4
        for _ in range(10):
            self.client.post(self.login_url, {
                "email": "test@example.com",
                "password": "wrongpass"
            }, REMOTE_ADDR='1.2.3.4', format="json")
    
        # jetzt gleicher IP, aber anderer User
        other_user = User.objects.create_user(email="other@example.com", password="SecurePassword123", is_active=True)
    
        response = self.client.post(self.login_url, {
            "email": "other@example.com",
            "password": "SecurePassword123"
        }, REMOTE_ADDR='1.2.3.4', format="json")
    
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_other_user_not_locked_out_with_other_ip(self):
        other_user = User.objects.create_user(email="other@example.com", password="SecurePassword123", is_active=True)

        response = self.client.post(self.login_url, {
            "email": "other@example.com",
            "password": "SecurePassword123"
        }, REMOTE_ADDR='5.6.7.8', format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

class ResetAxesLockoutTestCase(BaseLoginTestCase):
    def test_counter_resets_on_successful_login(self):
        # 6 Failed attempts
        for _ in range(6):
            self.client.post(self.login_url, {
                "email": self.email,
                "password": "wrongPassword"
            }, format="json")

        # 1 Successful login
        self.client.post(self.login_url, {
            "email": self.email,
            "password": self.password
        }, format="json")

        # Another 5 failed attempts - should not yet be blocked
        for _ in range(5):
            response = self.client.post(self.login_url, {
                "email": self.email,
                "password": "wrongPassword"
            }, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "E-mail or password is incorrect")

    def test_lockout_email_flag_resets_on_successful_login(self):
        user = User.objects.get(email=self.email)
        user.lockout_email_sent = True
        user.save()

        response = self.client.post(self.login_url, {
            "email": self.email,
            "password": self.password
        }, format="json")

        user.refresh_from_db()
        self.assertFalse(user.lockout_email_sent)