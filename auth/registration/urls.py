from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConfirmEmailView, RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("confirm-email/<int:uid>/<str:token>/", ConfirmEmailView.as_view(), name="confirm-email"),
]