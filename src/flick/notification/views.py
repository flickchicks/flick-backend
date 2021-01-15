import json
from user.models import Profile

from api import settings as api_settings
from api.utils import failure_response
from api.utils import success_response
from django.db.models import Q
from django.utils.dateparse import parse_datetime
from notification.models import Notification
from notification.serializers import NotificationSerializer
from rest_framework import generics


class NotificationList(generics.GenericAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def get(self, request):
        """See all notifications."""
        if not Profile.objects.filter(user=request.user):
            return failure_response(f"No user to be found with id of {request.user.id}.")
        profile = Profile.objects.get(user=request.user)
        notifs = Notification.objects.filter(Q(to_user=profile))
        serializer = self.serializer_class(notifs, many=True)
        return success_response(serializer.data)

    def post(self, request):
        """Update the last viewed notification time."""
        data = json.loads(request.body)
        notif_time_viewed = data.get("notif_time_viewed")
        if not Profile.objects.filter(user=request.user):
            return failure_response(f"No user to be found with id of {request.user.id}.")
        profile = Profile.objects.get(user=request.user)
        profile.notif_time_viewed = parse_datetime(notif_time_viewed)
        profile.save()
        return success_response({"notif_time_viewed": profile.notif_time_viewed})
