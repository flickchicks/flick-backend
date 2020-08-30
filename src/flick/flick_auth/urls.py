from django.urls import path

from .views import AuthenticateView
from .views import LoginView
from .views import LogoutView
from .views import RegisterView
from .views import UserView

urlpatterns = [
    path("me/", UserView.as_view(), name="me"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("authenticate/", AuthenticateView.as_view(), name="authenticate"),
]
