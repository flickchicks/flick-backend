from user.profile_simple_serializers import ProfileSimpleSerializer

from comment.serializers import SimpleCommentSerializer
from group.serializers import GroupSuperSimpleSerializer
from lst.simple_serializers import LstSimpleSerializer
from notification.models import Notification
from rest_framework import serializers
from suggestion.serializers import SimpleSuggestionSerializer


class NotificationSerializer(serializers.ModelSerializer):
    from_user = ProfileSimpleSerializer(many=False)
    to_user = ProfileSimpleSerializer(many=False)
    lst = LstSimpleSerializer(many=False)
    group = GroupSuperSimpleSerializer(many=False)
    suggestion = SimpleSuggestionSerializer(many=False)
    new_owner = ProfileSimpleSerializer(many=False)
    collaborators_added = ProfileSimpleSerializer(many=True)
    collaborators_removed = ProfileSimpleSerializer(many=True)
    comment = SimpleCommentSerializer(many=False)

    class Meta:
        model = Notification
        fields = (
            "id",
            "notif_type",
            "from_user",
            "to_user",
            "lst",
            "group",
            "comment",
            "suggestion",
            "new_owner",
            "num_shows_added",
            "num_shows_removed",
            "collaborators_added",
            "collaborators_removed",
            "created_at",
            "updated_at",
        )
        ready_only_fields = fields
