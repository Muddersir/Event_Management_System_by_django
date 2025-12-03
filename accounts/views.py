from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.tokens import default_token_generator
from .forms import SignupForm, LoginForm
from .tokens import account_activation_token
from django import forms

# We provide a wrapper around AuthenticationForm to prevent unactivated users
class CustomLoginForm(LoginForm):
    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError("Account is not activated. Check your email.", code="inactive")

def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # must activate by email
            user.save()
            # assign default 'Participant' group
            participant_group, _ = Group.objects.get_or_create(name="Participant")
            user.groups.add(participant_group)
            # activation email will be sent by accounts.signals (post_save)
            messages.success(request, "Account created. Check your email to activate your account.")
            return redirect("accounts:login")
    else:
        form = SignupForm()
    return render(request, "accounts/signup.html", {"form": form})


def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your account has been activated. You can now log in.")
        return redirect("accounts:login")
    else:
        return render(request, "accounts/activate_account.html", {"valid": False})