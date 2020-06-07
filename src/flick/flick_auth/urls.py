from django.urls import include, path

from .views import LoginView, LogoutView, RegisterView
from user.views import UserView

urlpatterns = [
    path("me/", UserView.as_view(), name="user"),
    # path('me/profile/', ProfileView.as_view(), name='profile'),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
]
