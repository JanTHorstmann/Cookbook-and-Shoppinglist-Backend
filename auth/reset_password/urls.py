from django.urls import path
from .views import ResetPasswordBruteForceView

urlpatterns = [
    path("resetpasswords/bruteforce/<uidb64>/<token>/", ResetPasswordBruteForceView.as_view(), name="resetpasswords"),
]