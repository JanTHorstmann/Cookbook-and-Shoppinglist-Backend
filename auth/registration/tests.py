from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class RegistrationTests(APITestCase):
    def setUp(self):
        self.url = reverse('register')

    def test_register_user_successfully(self):
        """Test successful user registration."""
        data = {
            "email": "newuser@example.com",
            "password": "SecurePass123!"
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

    def test_register_user_missing_email(self):
        """Test registration fails when email is missing."""
        data = {
            "email": "",
            "password": "SecurePass123!"
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_register_user_missing_password(self):
        """Test registration fails when password is missing."""
        data = {
            "email": "nopassword@example.com",
            "password": ""
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_register_user_duplicate_email(self):
        """Test registration fails when email already exists."""
        User.objects.create_user(
            email="existing@example.com",
            password="SomePassword123"
        )
        data = {
            "email": "existing@example.com",
            "password": "SecurePass123!"
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_register_user_invalid_email_format(self):
        """Test registration fails with invalid email format."""
        data = {
            "email": "invalid-email",
            "password": "SecurePass123!"
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    # def test_confirmation_email_is_sent(self):
    #     """Test that a confirmation email is sent after registration."""
    #     # Hier könnten wir das Email-Backend prüfen, wenn du willst.
    #     # Für jetzt prüfen wir einfach, ob Registrierung OK ist.
    #     data = {
    #         "email": "confirm@example.com",
    #         "username": "confirmuser",
    #         "password": "SecurePass123!"
    #     }
    #     with self.assertLogs('django.core.mail', level='INFO') as cm:
    #         response = self.client.post(self.url, data)
    #         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     # Hier könntest du noch in cm.output prüfen, ob eine Mail geloggt wurde.