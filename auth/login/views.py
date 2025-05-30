
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from .serializers import LoginSerializer
from decouple import config
from axes.handlers.proxy import AxesProxyHandler
from axes.utils import reset

User = get_user_model()

class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email'].lower()
            password = serializer.validated_data['password']
            if AxesProxyHandler.is_locked(request) or AxesProxyHandler.is_locked(request, credentials={"email": email}):

                user = User.objects.get(email=email)
                if user and not user.lockout_email_sent:
                    self.send_reset_password_link(user)
                    user.lockout_email_sent = True
                    user.save()

                return Response(
                    {"detail": "Too many failed login attempts. Please check your emails"},
                    status=status.HTTP_403_FORBIDDEN
                )
            user = authenticate(request=request, email=email, password=password)
            if user is not None:
                reset(username=user.email)
                refresh = RefreshToken.for_user(user)
                user.lockout_email_sent = False
                user.save()
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            else:    
                user = User.objects.filter(email=email).first()
                if user and user.check_password(password):
                    if not user.is_active:
                        return Response({'detail': 'Email is not confirmed'}, status=status.HTTP_401_UNAUTHORIZED)      
                return Response({'detail': 'E-mail or password is incorrect'}, status=status.HTTP_401_UNAUTHORIZED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def send_reset_password_link(self, user):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        reset_url = f"{config('FRONTEND_URL')}/reset-password-brute-force/{uid}/{token}/"
        subject = "Too many login attempts - Reset your password"
        user_name = user.email.split("@")[0].capitalize()
    
        html_message = render_to_string("email_reset_password_bruteforce.html", {
            "user_name": user_name,
            "reset_url": reset_url
        })

        text_message = f"Hi {user_name},\n\nClick the link to activate your account:\n{reset_url}"

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=config("DEFAULT_FROM_EMAIL"),
            to=[user.email],
        )
        email.attach_alternative(html_message, "text/html")
        email.send()
    
class ProtectedTestView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({"message": f"Hello, {request.user.email.split('@')[0].capitalize()}!"})
