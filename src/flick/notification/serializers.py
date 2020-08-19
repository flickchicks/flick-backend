from user.profile_simple_serializers import ProfileSimpleSerializer

from lst.simple_serializers import LstSimpleSerializer
from notification.models import Notification
from rest_framework import serializers


class NotificationSerializer(serializers.ModelSerializer):
    from_user = ProfileSimpleSerializer(many=False)
    to_user = ProfileSimpleSerializer(many=False)
    lst = LstSimpleSerializer(many=False)

    class Meta:
        model = Notification
        fields = (
            "notif_type",
            "from_user",
            "to_user",
            "lst",
            "num_shows_added",
            "num_shows_removed",
            "friend_request_accepted",
            "created_at",
        )
        ready_only_fields = fields
