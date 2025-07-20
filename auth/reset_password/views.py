from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_str, force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import ResetPasswordSerializer, SendResetPasswordMailSerializer, ResetPasswordIfLoggedInSerializer
from axes.utils import reset
from decouple import config
from auth.registration.utils import account_activation_token

User = get_user_model()
class ResetPasswordView(APIView):
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'detail': 'Invalid link'}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({'detail': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.validated_data['password'])
            reset(username=user.email)
            user.save()
            return Response({'detail': 'Password reset successful'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SendResetPasswordMailView(APIView):
    def post(self, request):
        serializer = SendResetPasswordMailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email'].lower()
            user = User.objects.get(email=email)
            if user is not None:
                if user.is_active:
                    self.send_reset_password_link(user)
                else:
                    return Response({'detail': 'Account is not yet confirmed - confirmation email sent again'}, status=status.HTTP_200_OK)
            else:
                pass
            return Response({'detail': 'Send e-mail succesful'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'No valid email'}, status=status.HTTP_400_BAD_REQUEST)
        
    def send_reset_password_link(self, user):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        reset_url = f"{config('FRONTEND_URL')}/forget-password-reset/{uid}/{token}/"
        subject = "You have forgotten your password - Reset your password"
        user_name = user.email.split("@")[0].capitalize()
    
        html_message = render_to_string("email_reset_password.html", {
            "user_name": user_name,
            "reset_url": reset_url
        })

        text_message = f"Hi {user_name},\n\nClick the link to reset your password:\n{reset_url}"

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=config("DEFAULT_FROM_EMAIL"),
            to=[user.email],
        )
        email.attach_alternative(html_message, "text/html")
        email.send()

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

class ResetPasswordIfLoggedInView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ResetPasswordIfLoggedInSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['password_old']):
                return Response({'detail': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data['password_new'])
            user.save()
            self.send_confirmation_email(user)
            return Response({'detail': 'Password reset successful'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def send_confirmation_email(self, user):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        reset_url = f"{config('FRONTEND_URL')}/forget-password-reset/{uid}/{token}/"
        subject = "Password successfully changed"
        user_name = user.email.split("@")[0].capitalize()
    
        html_message = render_to_string("email_reset_password_confirmation.html", {
            "user_name": user_name,
            "reset_url": reset_url
        })
        
        text_message = f"Hi {user_name}, \n\nYour password has been successfully changed. \n\nIf you have not changed your password, please change it immediately using the following link : \n\n{reset_url}"

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=config("DEFAULT_FROM_EMAIL"),
            to=[user.email],
        )
        email.attach_alternative(html_message, "text/html")
        email.send()
            