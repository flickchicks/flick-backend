from django.db import models

from django.contrib.auth.models import User


# Create your models here.
class Profile(models.Model):
    """
    User profile model. Matches one to one with built-in Django user model.
    """
    profile_pic = models.TextField()
    phone_number = models.TextField()
    social_id_token_type = models.TextField()
    social_id_token = models.TextField()

    def __str__(self):
        return f"{self.username}, {self.name}"

