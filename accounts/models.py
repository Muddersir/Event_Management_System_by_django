from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.conf import settings
import os

def user_profile_image_path(instance, filename):
    return os.path.join("users", f"user_{instance.pk}", filename)

def default_user_image():
    return "default-user.png"

phone_validator = RegexValidator(
    regex=r'^\+?\d{7,15}$',
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=16, validators=[phone_validator], blank=True, null=True)
    profile_image = models.ImageField(upload_to=user_profile_image_path, default=default_user_image, blank=True)

    def __str__(self):
        return self.get_full_name() or self.username