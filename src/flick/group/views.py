import json
from user.models import Profile

from api import settings as api_settings
from api.utils import failure_response
from api.utils import success_response
from rest_framework import generics

from .models import Group
from .serializers import GroupSerializer
from .serializers import GroupSimpleSerializer


class GroupList(generics.GenericAPIView):

    serializer_class = GroupSimpleSerializer
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def get(self, request):
        """See all groups that request.user belongs to."""
        if not Profile.objects.filter(user=request.user).exists():
            return failure_response(f"No user to be found with id of {request.user.id}.")
        profile = Profile.objects.get(user=request.user)
        groups = Group.objects.filter(members=profile)
        serializer = self.serializer_class(groups, many=True)
        return success_response(serializer.data)

    def post(self, request):
        """Create a group."""
        if not Profile.objects.filter(user=request.user).exists():
            return failure_response(f"No user to be found with id of {request.user.id}.")
        profile = Profile.objects.get(user=request.user)
        data = json.loads(request.body)
        member_ids = data.get("members")
        group = Group.objects.create(name=data.get("name"))
        group.members.add(profile)
        for member_id in member_ids:
            member_profile_exists = Profile.objects.filter(user__id=member_id).exists()
            if not member_profile_exists:
                continue
            member_profile = Profile.objects.get(user__id=member_id)
            group.members.add(member_profile)
        group.save()
        serializer = self.serializer_class(group)
        return success_response(serializer.data)


class GroupDetail(generics.GenericAPIView):
    serializer_class = GroupSerializer
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def get(self, request, pk):
        """Get a group by id. If request.user does not belong to the group, return a failure response."""
        if not Profile.objects.filter(user=request.user).exists():
            return failure_response(f"No user to be found with id of {request.user.id}.")
        profile = Profile.objects.get(user=request.user)
        if not profile.groups.filter(id=pk).exists():
            return failure_response(f"User does not belong to group with id {pk} or group with id {pk} does not exist.")
        group = profile.groups.get(id=pk)
        serializer = self.serializer_class(group)
        return success_response(serializer.data)

    def post(self, request, pk):
        """Update a group by id. For now, only supports renaming."""
        pass
