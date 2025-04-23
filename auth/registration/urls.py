from django.urls import path
from .views import ConfirmEmailView, RegisterViewSet

urlpatterns = [
    path("confirm-email/<int:uid>/<str:token>/", ConfirmEmailView.as_view(), name="confirm-email"),
]