from django.db import models
from django.contrib.auth.models import AbstractBaseUser

class CustomUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
