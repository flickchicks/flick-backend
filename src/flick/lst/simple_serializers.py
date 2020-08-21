from user.profile_simple_serializers import ProfileSimpleSerializer

from rest_framework import serializers
from show.simple_serializers import ShowSimplestSerializer

from .models import Lst


class LstSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lst
        fields = ("id", "name", "pic", "is_saved", "is_private", "is_watch_later")
        read_only_fields = fields


class MeLstSerializer(serializers.ModelSerializer):
    collaborators = ProfileSimpleSerializer(many=True)
    shows = serializers.SerializerMethodField("get_subset_of_shows")

    def get_subset_of_shows(self, obj):
        shows = obj.shows.all()[:10]
        return ShowSimplestSerializer(instance=shows, many=True).data

    class Meta:
        model = Lst
        fields = ("id", "name", "is_private", "collaborators", "shows")
        read_only_fields = fields
