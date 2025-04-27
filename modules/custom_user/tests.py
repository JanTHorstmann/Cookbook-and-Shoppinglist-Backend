from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserCreationTests(TestCase):
    def test_create_user_with_email_successful(self):
        """
        Tests whether a user with a valid e-mail and password is created correctly.
        """
        email = 'user@example.com'
        password = 'testpass123'
        user = User.objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_user_email_is_lowercase_on_save(self):
        """
        Tests that emails are saved in lowercase, even after changes.
        """
        user = User.objects.create_user(email="lowercase@domain.com", password="test123")
        user.email = "UpperCase@Domain.COM"
        user.save()
        self.assertEqual(user.email, "uppercase@domain.com")

    def test_user_email_is_stripped_and_lowered(self):
        """
        Tests that leading/trailing spaces are removed and email is lowercased.
        """
        user = User.objects.create_user(email="  Spaced@Example.com  ", password="test123")
        self.assertEqual(user.email, "spaced@example.com")

    def test_user_email_normalized(self):
        """
        Checks whether the e-mail is automatically converted to lower case when it is saved.
        """
        user = User.objects.create_user(email="Test@Example.com", password="password123")
        self.assertEqual(user.email, "test@example.com")

    def test_create_user_without_email_raises_error(self):
        """
        If no e-mail is specified, an error should be thrown.
        """
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='pass1234')
    
    def test_duplicate_email_raises_error(self):
        User.objects.create_user(email="duplicate@example.com", password="pass123")
        with self.assertRaises(Exception):
            User.objects.create_user(email="duplicate@example.com", password="pass456")

    def test_create_user_with_password_none_raises_error(self):
        """
        If no password is provided, a ValueError should be raised.
        """
        with self.assertRaises(ValueError):                                     ## wirft noch einen Fehler
            User.objects.create_user(email="user@example.com", password=None)

    def test_user_str_returns_email(self):
        user = User.objects.create_user(email="test@example.com", password="pass")
        self.assertEqual(str(user), "test@example.com")


class SuperUserCreationTests(TestCase):
    def test_create_superuser_successful(self):
        """
        Ensures that a superuser is created correctly and that the corresponding flags are set.
        """
        email = 'admin@example.com'
        password = 'adminpass123'
        superuser = User.objects.create_superuser(email=email, password=password)

        self.assertEqual(superuser.email, email)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_active)

    def test_create_superuser_with_invalid_flags_raises_error(self):
        """
        If you try to create a superuser without is_staff=True or is_superuser=True, this should fail.
        """
        with self.assertRaises(ValueError):
            User.objects.create_superuser(email='admin@example.com', password='admin', is_staff=False)

        with self.assertRaises(ValueError):
            User.objects.create_superuser(email='admin@example.com', password='admin', is_superuser=False)