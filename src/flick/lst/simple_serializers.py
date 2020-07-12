from rest_framework import serializers

from .models import Lst


class LstSimpleSerializer(serializers.ModelSerializer):
    # shows = ShowSerializer(many=True)
    lst_id = serializers.CharField(source="id")

    class Meta:
        model = Lst
        fields = ("lst_id", "lst_name", "lst_pic", "is_saved", "is_private", "is_watch_later")
        read_only_fields = fields
