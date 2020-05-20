from django.db import models

# Create your models here.
class FlickAccount(models.Model):
    username = models.CharField(max_length=30, unique=True) # max_length required for char field
    name = models.CharField(max_length=60)
    profile_pic = models.TextField()
    phone_number = models.TextField()
    social_id_token_type = models.TextField()
    social_id_token = models.TextField()
