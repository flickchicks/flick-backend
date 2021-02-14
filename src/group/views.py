import datetime
import json
from user.models import Profile

from api import settings as api_settings
from api.utils import success_response
import pytz
from rest_framework import generics
from show.models import Show
from show.serializers import GroupShowSerializer
from show.serializers import ShowSerializer
from vote.serializers import VoteSerializer

from .models import Group
from .serializers import GroupSerializer
from .serializers import GroupSimpleSerializer
from .tasks import clear_shows
from .tasks import create_new_group_notif
from .tasks import vote


class GroupList(generics.GenericAPIView):

    serializer_class = GroupSimpleSerializer
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def get(self, request):
        """See all groups that request.user belongs to."""
        profile = Profile.objects.get(user=request.user)
        groups = Group.objects.filter(members=profile)
        serializer = self.serializer_class(groups, many=True)
        return success_response(serializer.data)

    def post(self, request):
        """Create a group."""
        profile = Profile.objects.get(user=request.user)
        data = json.loads(request.body)
        member_ids = data.get("members", [])
        group = Group.objects.create(name=data.get("name"))
        group.members.add(profile)
        for member_id in member_ids:
            try:
                member_profile = Profile.objects.get(user__id=member_id)
                group.members.add(member_profile)
            except:
                continue
        group.save()
        create_new_group_notif.delay(profile_id=profile.id, group_id=group.id, member_ids=member_ids)
        serializer = self.serializer_class(group)
        return success_response(serializer.data)


class GroupDetail(generics.GenericAPIView):
    serializer_class = GroupSerializer
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def get(self, request, pk):
        """Get a group by id. If request.user does not belong to the group, return a failure response."""
        profile = Profile.objects.get(user=request.user)
        group = profile.groups.get(id=pk)
        serializer = self.serializer_class(group)
        return success_response(serializer.data)

    def post(self, request, pk):
        """Update a group by id. For now, only supports renaming."""
        profile = Profile.objects.get(user=request.user)
        group = profile.groups.get(id=pk)
        data = json.loads(request.body)
        group.name = data.get("name")
        group.save()
        serializer = self.serializer_class(group)
        return success_response(serializer.data)


class GroupDetailAdd(generics.GenericAPIView):
    serializer_class = GroupSerializer
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def post(self, request, pk):
        """Update a group by id by adding members and shows."""
        profile = Profile.objects.get(user=request.user)
        group = profile.groups.get(id=pk)
        data = json.loads(request.body)
        member_ids = data.get("members", [])
        show_ids = data.get("shows", [])
        for member_id in member_ids:
            try:
                member_profile = Profile.objects.get(user__id=member_id)
                group.members.add(member_profile)
            except:
                continue
        for show_id in show_ids:
            try:
                show = Show.objects.get(id=show_id)
                group.shows.add(show)
            except:
                continue
        group.save()
        create_new_group_notif.delay(profile_id=profile.id, group_id=group.id, member_ids=member_ids)
        serializer = self.serializer_class(group)
        return success_response(serializer.data)


class GroupDetailRemove(generics.GenericAPIView):
    serializer_class = GroupSerializer
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def post(self, request, pk):
        """Update a group by id by removing members and shows."""
        profile = Profile.objects.get(user=request.user)
        group = profile.groups.get(id=pk)
        data = json.loads(request.body)
        member_ids = data.get("members", [])
        show_ids = data.get("shows", [])
        for member_id in member_ids:
            try:
                member_profile = Profile.objects.get(user__id=member_id)
                group.members.remove(member_profile)
            except:
                continue
        for show_id in show_ids:
            try:
                show = Show.objects.get(id=show_id)
                group.shows.remove(show)
            except:
                continue
        group.save()
        serializer = self.serializer_class(group)
        return success_response(serializer.data)


class GroupClearShows(generics.GenericAPIView):
    serializer_class = GroupSerializer
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def post(self, request, pk):
        """Clear all shows in a group by id."""
        clear_shows.delay(user_id=request.user.id, group_id=pk)
        return success_response()


class GroupShowList(generics.GenericAPIView):
    serializer_class = GroupShowSerializer
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def order(self, result):
        return 1 * result["num_yes_votes"] + 0.5 * result["num_maybe_votes"] - 1 * result["num_no_votes"]

    def get(self, request, pk):
        """View show results in a group by id."""
        profile = Profile.objects.get(user=request.user)
        group = profile.groups.get(id=pk)
        num_members = group.members.count()
        num_voted = 0
        for member in group.members.all():
            if group.votes.filter(voter=member).exists():
                num_voted += 1
        user_voted = group.votes.filter(voter=profile).count() > 0
        serializer = self.serializer_class(group.shows.all(), context={"group_id": group.id}, many=True)
        data = {
            "num_members": num_members,
            "num_voted": num_voted,
            "user_voted": user_voted,
            "results": sorted(serializer.data, key=self.order, reverse=True),
        }
        return success_response(data)


class GroupPendingList(generics.GenericAPIView):
    serializer_class = ShowSerializer
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def get(self, request, pk):
        """Get the list of the user's pending (not yet voted) shows in a group by id."""
        # timestamp needed for frontend to not show old results if we return them slower than
        # the users vote
        request_timestamp = datetime.datetime.now(tz=pytz.utc)
        profile = Profile.objects.get(user=request.user)
        group = profile.groups.get(id=pk)
        voted_show_ids = group.votes.filter(voter=profile).values_list("show", flat=True)
        all_show_ids = group.shows.all().values_list("id", flat=True)
        pending_show_ids = all_show_ids.difference(voted_show_ids)
        serializer = self.serializer_class(
            group.shows.filter(id__in=pending_show_ids), context={"request": self.request}, many=True
        )
        data = {"request_timestamp": request_timestamp, "shows": serializer.data}
        return success_response(data)


class GroupVoteShow(generics.GenericAPIView):
    serializer_class = VoteSerializer
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def post(self, request, group_pk, show_pk):
        """Vote for a show in a group by id."""
        vote.delay(request.body, request.user.id, group_pk, show_pk)
        return success_response()
