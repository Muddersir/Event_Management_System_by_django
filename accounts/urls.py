from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "accounts"

urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("activate/<uidb64>/<token>/", views.activate_account, name="activate"),
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html", authentication_form=views.CustomLoginForm), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]