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
from .utils import account_activation_token
import django.contrib.auth.password_validation as validators
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

User = get_user_model()

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

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

        user.save()
        self.send_confirmation_email(user)
        return user

    def send_confirmation_email(self, user):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)

        confirmation_url = f"{config('FRONTEND_URL')}/api/registration/confirm-email/{uid}/{token}/"

        subject = "Confirm your email address"
        user_name = user.email.split("@")[0].capitalize()
    
        html_message = render_to_string("email_confirmation.html", {
            "user_name": user_name,
            "confirmation_url": confirmation_url
        })

        # Nur für Fallback-Text-E-Mail (optional)
        text_message = f"Hi {user_name},\n\nClick the link to activate your account:\n{confirmation_url}"

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=config("DEFAULT_FROM_EMAIL"),
            to=[user.email],
        )
        email.attach_alternative(html_message, "text/html")
        email.send()