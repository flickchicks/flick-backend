from user.profile_simple_serializers import ProfileSimpleSerializer

from lst.simple_serializers import LstSimpleSerializer
from notification.models import Notification
from rest_framework import serializers


class NotificationSerializer(serializers.ModelSerializer):
    from_user = ProfileSimpleSerializer(many=False)
    to_user = ProfileSimpleSerializer(many=False)
    lst = LstSimpleSerializer(many=False)
    new_owner = ProfileSimpleSerializer(many=False)
    collaborators_added = ProfileSimpleSerializer(many=True)
    collaborators_removed = ProfileSimpleSerializer(many=True)

    class Meta:
        model = Notification
        fields = (
            "id",
            "notif_type",
            "from_user",
            "to_user",
            "lst",
            "new_owner",
            "num_shows_added",
            "num_shows_removed",
            "incoming_friend_request_accepted",
            "outgoing_friend_request_accepted",
            "collaborators_added",
            "collaborators_removed",
            "created_at",
            "updated_at",
        )
        ready_only_fields = fields
