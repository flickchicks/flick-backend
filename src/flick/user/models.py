from django.db import models

from django.contrib.auth.models import User

from asset.models import AssetBundle


# Create your models here.
class Profile(models.Model):
    """
    User profile model. Matches one to one with built-in Django user model.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    # profile_pic = models.ForeignKey(AssetBundle, on_delete=models.CASCADE)
    phone_number = models.TextField()
    social_id_token_type = models.TextField()
    social_id_token = models.TextField()
    
    # override what django admin displays
    def __str__(self):
        return f"{self.user.username}, {self.user.name}"

