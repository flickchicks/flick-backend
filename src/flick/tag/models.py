from django.db import models


class Tag(models.Model):
    tag = models.CharField(max_length=100, unique=True)
    # shows = models.ManyToManyField(Show, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def shows(self, obj):
        res = []
        print(obj.shows.all())
        for show in obj.shows.all():
            print(f"show: {show}")
            print(f"show.title: {show.title}")
            res += show.title
        return res
