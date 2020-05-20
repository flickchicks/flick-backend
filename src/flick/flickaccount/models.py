from django.db import models

# Create your models here.
class FlickAccount(models.Model):
    username = models.TextField()
    name = models.TextField()
    profile_pic = models.TextField()
    phone_number = models.TextField()
    social_id_token_type = models.TextField()
    social_id_token = models.TextField()
