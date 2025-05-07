
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
from .serializers import LoginSerializer
from rest_framework.permissions import IsAuthenticated
from axes.handlers.proxy import AxesProxyHandler

User = get_user_model()

class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email'].lower()
            password = serializer.validated_data['password']
            if AxesProxyHandler.is_locked(request) or AxesProxyHandler.is_locked(request, credentials={"email": email}):
                return Response(
                    {"detail": "Too many failed login attempts. Please try again in 30 minutes."},
                    status=status.HTTP_403_FORBIDDEN
                )
            user = authenticate(request=request, email=email, password=password)
            if user is not None:
                if not user.is_active:
                    return Response({'detail': 'Email is not confirmed'}, status=status.HTTP_401_UNAUTHORIZED)
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            else:
                return Response({'detail': 'E-mail or password is incorrect'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ProtectedTestView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({"message": f"Hello, {request.user.email.split('@')[0].capitalize()}!"})
