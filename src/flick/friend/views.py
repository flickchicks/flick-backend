import json
from user.models import Profile

from api import settings as api_settings
from api.utils import failure_response
from api.utils import success_response
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from friend.serializers import FriendRequestSerializer
from friend.serializers import FriendshipSerializer
from friend.serializers import FriendUserSerializer
from friend.serializers import IncomingRequestSerializer
from friendship.models import Friend
from friendship.models import FriendshipRequest
from notification.models import Notification
from push_notifications.models import APNSDevice
from push_notifications.models import GCMDevice
from rest_framework import generics
from rest_framework.views import APIView


class FriendList(APIView):
    """
    List all friends.
    """

    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def get(self, request, format=None):
        friends = [User.objects.get(id=friend.id) for friend in Friend.objects.friends(user=request.user)]
        serializer = FriendUserSerializer(friends, many=True)
        return success_response(serializer.data)


class UserFriendList(APIView):
    """
    List of all friends of a user.
    """

    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def get(self, request, pk, format=None):
        if request.user.id == pk:
            return HttpResponseRedirect(reverse("friend-list"))
        if not User.objects.filter(id=pk):
            return failure_response(f"User of id {pk} not found.")
        user = User.objects.get(id=pk)
        friends = [User.objects.get(id=friend.id) for friend in Friend.objects.friends(user=user)]
        serializer = FriendUserSerializer(friends, many=True)
        return success_response(serializer.data)


class FriendRequestListAndCreate(generics.ListCreateAPIView):
    """
    List and create friend requests.
    """

    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def get(self, request, format=None):
        friend_requests = Friend.objects.sent_requests(user=request.user)
        serializer = FriendRequestSerializer(friend_requests, many=True)
        return success_response(serializer.data)

    def post(self, request, format=None):
        data = json.loads(request.body)
        friend_requests = []
        for friend_id in data.get("ids"):
            try:
                friend = User.objects.get(id=friend_id)
                friend_requests.append(Friend.objects.add_friend(request.user, friend))
                ios_devices = APNSDevice.objects.filter(user=friend, active=True)
                android_devices = GCMDevice.objects.filter(user=friend, active=True)
                message_body = f"({friend.username}): {request.user.first_name} (@{request.user.username}) sent you a friend request."
                ios_devices.send_message(message={"body": message_body})
                android_devices.send_message(message={"body": message_body})
            except Exception as e:
                print(str(e))
                continue
        serializer = FriendRequestSerializer(friend_requests, many=True)
        return success_response(serializer.data)


class FriendAcceptListAndCreate(generics.ListCreateAPIView):
    """
    List and create friend requests.
    """

    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def _create_incoming_friend_request_accepted_for_to_user(self, from_user, to_user):
        from_user = Profile.objects.get(user=from_user)
        to_user = Profile.objects.get(user=to_user)
        notif = Notification()
        notif.notif_type = "incoming_friend_request_accepted"
        notif.from_user = from_user
        notif.to_user = to_user
        notif.save()

    def _create_outgoing_friend_request_accepted_for_from_user(self, from_user, to_user):
        from_user = Profile.objects.get(user=from_user)
        to_user = Profile.objects.get(user=to_user)
        notif = Notification()
        notif.notif_type = "outgoing_friend_request_accepted"
        notif.from_user = to_user
        notif.to_user = from_user
        notif.save()
        ios_devices = APNSDevice.objects.filter(user=to_user, active=True)
        android_devices = GCMDevice.objects.filter(user=to_user, active=True)
        message_body = (
            f"({to_user.username}): {from_user.first_name} (@{from_user.username}) accepted your friend request."
        )
        ios_devices.send_message(message={"body": message_body})
        android_devices.send_message(message={"body": message_body})

    def get(self, request, format=None):
        friend_requests = Friend.objects.unrejected_requests(user=request.user)
        serializer = IncomingRequestSerializer(friend_requests, many=True)
        return success_response(serializer.data)

    def post(self, request, format=None):
        data = json.loads(request.body)
        friends_accepted = []
        for friend_id in data.get("ids"):
            try:
                friend = User.objects.get(id=friend_id)
                id = request.user.id
                friend_request = FriendshipRequest.objects.get(from_user=friend.id, to_user=id)
                friend_request.accept()
                friends_accepted.append(friend_request)
                self._create_outgoing_friend_request_accepted_for_from_user(from_user=friend, to_user=request.user)
                self._create_incoming_friend_request_accepted_for_to_user(from_user=friend, to_user=request.user)
            except Exception as e:
                print(str(e))
                continue

        serializer = FriendshipSerializer(friends_accepted, many=True)

        return success_response(serializer.data)


class FriendRejectListAndCreate(generics.ListCreateAPIView):
    """
    List and create friend requests.
    """

    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def get(self, request, format=None):
        friend_requests = Friend.objects.rejected_requests(user=request.user)
        serializer = FriendRequestSerializer(friend_requests, many=True)
        return success_response(serializer.data)

    def post(self, request, format=None):
        data = json.loads(request.body)
        friends_rejected = []
        for friend_id in data.get("ids"):
            friend = User.objects.get(id=friend_id)
            id = request.user.id
            friend_request = FriendshipRequest.objects.get(from_user=friend.id, to_user=id)
            friend_request.reject()
            friends_rejected.append(friend_request)

        serializer = FriendRequestSerializer(friends_rejected, many=True)

        return success_response(serializer.data)


class FriendRemoveListAndCreate(generics.ListCreateAPIView):
    """
    List and create friend requests.
    """

    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def post(self, request, format=None):
        data = json.loads(request.body)
        friends_removed = []
        for friend_id in data.get("ids"):
            try:
                friend = User.objects.get(id=friend_id)
                Friend.objects.remove_friend(request.user, friend)
                friends_removed.append(friend)
            except Exception as e:
                print(str(e))
                continue

        serializer = FriendUserSerializer(friends_removed, many=True)

        return success_response(serializer.data)
