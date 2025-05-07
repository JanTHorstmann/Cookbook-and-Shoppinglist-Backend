from django.urls import path
from .views import LoginView, ProtectedTestView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("test/", ProtectedTestView.as_view(), name="test"),
]