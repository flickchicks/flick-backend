import json
from user.models import Profile

from api import settings as api_settings
from api.utils import failure_response
from api.utils import success_response
from django.db.models import Q
from django.utils.dateparse import parse_datetime
from notification.models import Notification
from notification.serializers import NotificationSerializer
from push_notifications.models import APNSDevice
from push_notifications.models import GCMDevice
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


class NotificationTest(generics.GenericAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def post(self, request):
        """Test endpoint for clients to send notifications."""
        data = json.loads(request.body)
        device_type = data.get("device_type")
        device_token = data.get("device_token")
        if not device_type or device_type not in ["ios", "android"]:
            return failure_response("Must supply device_type field, either 'ios' or 'android'.")
        if not device_token:
            return failure_response(
                "Must supply device_token field, for android this is the Firebase Cloud Messaging (FCM) registration id or the Apple Push Notification Service (APNS) token for the device."
            )
        if device_type == "ios":
            device = APNSDevice.objects.create(registration_id=device_token, user=request.user)
            device.send_message(message={"title": "Test Flick APNS Notification", "body": "Success!"})
            return success_response("Should have received a notification with title 'Test Flick Notification'")
        if device_type == "android":
            device = GCMDevice.objects.create(registration_id=device_token, cloud_message_type="FCM", user=request.user)
            device.send_message(message={"title": "Test Flick FCM Notification", "body": "Success!"})
            return success_response("Should have received a notification with title 'Test Flick Notification'")
        return failure_response("Could not send a notification.")


class NotificationEnable(generics.GenericAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def post(self, request):
        """Test endpoint for clients to send notifications."""
        data = json.loads(request.body)
        device_type = data.get("device_type")
        device_token = data.get("device_token")
        if not device_type or device_type not in ["ios", "android"]:
            return failure_response("Must supply device_type field, either 'ios' or 'android'.")
        if not device_token:
            return failure_response(
                "Must supply device_token field, for android this is the Firebase Cloud Messaging (FCM) registration id or the Apple Push Notification Service (APNS) token for the device."
            )
        if device_type == "ios":
            APNSDevice.objects.create(registration_id=device_token, user=request.user, active=True)
            return success_response(f"Enabled notifications for user {request.user}")
        if device_type == "android":
            GCMDevice.objects.create(
                registration_id=device_token, cloud_message_type="FCM", user=request.user, active=True
            )
            return success_response(f"Enabled notifications for user {request.user}")
        return failure_response(f"Could not enable notifications for user {request.user}.")
