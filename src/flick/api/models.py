from django.db import models

from django.contrib.auth.models import User

# Create your models here.
class Item(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    like_count = models.IntegerField(default=0)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property # can get via item.full_title instead of item.full_title()
    def full_title(self):
        if self.subtitle:
            return f"{self.title}: {self.subtitle}"
        return self.title

    @property
    def owner_email(self):
        return self.owner.email

    def __unicode__(self):
        return self.title