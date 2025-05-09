from django.urls import path
from .views import ResetPasswordView, SendResetPasswordMailView

urlpatterns = [
    path("resetpasswords/<uidb64>/<token>/", ResetPasswordView.as_view(), name="resetpasswordsbruteforce"),
    path("sendresetpasswordmail/", SendResetPasswordMailView.as_view(), name="sendresetpasswordmail"),
]