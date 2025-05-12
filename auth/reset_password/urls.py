from django.urls import path
from .views import ResetPasswordView, SendResetPasswordMailView, ResetPasswordIfLoggedInView

urlpatterns = [
    path("resetpasswords/<uidb64>/<token>/", ResetPasswordView.as_view(), name="resetpasswords"),
    path("sendresetpasswordmail/", SendResetPasswordMailView.as_view(), name="sendresetpasswordmail"),
    path("resetpasswordmailifloggedin/", ResetPasswordIfLoggedInView.as_view(), name="resetpasswordmailifloggedin"),
]