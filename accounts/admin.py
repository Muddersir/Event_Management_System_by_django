from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from .models import CustomUser

class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = "__all__"

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        ("Profile", {"fields": ("phone_number", "profile_image")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Profile", {"fields": ("phone_number", "profile_image")}),
    )
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "phone_number")

admin.site.register(CustomUser, CustomUserAdmin)
