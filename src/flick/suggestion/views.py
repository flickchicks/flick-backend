import json
from user.models import Profile

from api import settings as api_settings
from api.utils import failure_response
from api.utils import success_response
from django.contrib.auth.models import User
from friendship.models import Friend
from rest_framework import generics
from show.models import Show

from .models import PrivateSuggestion
from .serializers import PrivateSuggestionSerializer


class PrivateSuggesionView(generics.GenericAPIView):
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def get(self, request):
        user = request.user
        suggestions = user.suggestions_received.all()
        suggestion_data = PrivateSuggestionSerializer(suggestions, many=True)
        return success_response(suggestion_data.data)

    def post(self, request):
        data = json.loads(request.body)
        user = request.user
        if not Profile.objects.filter(user=user):
            return failure_response(f"{user} must be logged in.")
        profile = Profile.objects.get(user=user)

        show_id = data.get("show_id")
        if not Show.objects.filter(id=show_id):
            return failure_response(f"Show of id {show_id} does not exist.")
        show = Show.objects.get(id=data.get("show_id"))

        suggestions = []
        for friend_id in data.get("user_ids"):
            try:
                if friend_id == user.pk:
                    raise Exception("Unable suggest to yourself")
                if not User.objects.filter(id=friend_id):
                    raise Exception(f"Friend ID {friend_id} does not correspond to a valid user")
                friend = User.objects.get(id=friend_id)
                if not Friend.objects.are_friends(user, friend):
                    raise Exception("Unable to suggest to users that are not your friend")
                pri_suggestion = PrivateSuggestion()
                pri_suggestion.from_user = profile
                pri_suggestion.to_user = friend
                pri_suggestion.show = show
                if data.get("message"):
                    pri_suggestion.message = data.get("message")

                pri_suggestion.save()
                suggestions.append(pri_suggestion)
            except Exception as e:
                print(str(e))
                continue

        suggestion_data = PrivateSuggestionSerializer(suggestions, many=True)
        return success_response(suggestion_data.data)
