import json
from user.models import Profile
from user.serializers import FriendProfileSerializer

from api import settings as api_settings
from api.utils import failure_response
from api.utils import success_response
from django.contrib.auth.models import User
from friend.serializers import FriendRequestSerializer
from friend.serializers import FriendshipSerializer
from friend.serializers import FriendUserSerializer
from friend.serializers import IncomingRequestSerializer
from friendship.models import Friend
from friendship.models import FriendshipRequest
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
                user = User.objects.get(id=friend_id)
                friend_requests.append(Friend.objects.add_friend(request.user, user))
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
                print(e)
                continue

        serializer = FriendUserSerializer(friends_removed, many=True)

        return success_response(serializer.data)


class FriendUserView(generics.GenericAPIView):
    model = Profile
    serializer_class = FriendProfileSerializer
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def get(self, request, pk):
        if not User.objects.filter(id=pk):
            return failure_response(f"User of id {pk} not found.")
        profile = Profile.objects.get(user_id=pk)
        return success_response(FriendProfileSerializer(profile).data)
