from django.urls import path
from .views import ResetPasswordBruteForceView

urlpatterns = [
    path("resetpasswords/bruteforce/", ResetPasswordBruteForceView.as_view(), name="resetpasswords"),
]