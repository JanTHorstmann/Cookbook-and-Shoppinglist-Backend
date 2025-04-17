from rest_framework import serializers
from django.core import exceptions
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.conf import settings
from decouple import config
import django.contrib.auth.password_validation as validators

User = get_user_model()

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    is_superuser = serializers.BooleanField(default=False)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email already exists.")
        return value

    def validate(self, data):
        user = User(email=data["email"])
        password = data.get('password')

        try:
            validators.validate_password(password=password, user=user)
        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
        )
        if validated_data.get("is_superuser"):
            user.is_superuser = True
            user.is_staff = True

        user.save()
        self.send_confirmation_email(user)
        return user

    def send_confirmation_email(self, user):
        token = default_token_generator.make_token(user)
        uid = user.pk  # oder mit base64 kodieren, wenn du willst

        confirmation_url = f"{config('FRONTEND_URL')}/confirm-email/{uid}/{token}/"

        send_mail(
            subject="Confirm your email",
            message=f"Please confirm your email by clicking the following link:\n\n{confirmation_url}",
            from_email=config('DEFAULT_FROM_EMAIL'),
            recipient_list=[user.email],
            fail_silently=False,
        )