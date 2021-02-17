import json
from user.models import Profile

from api import settings as api_settings
from api.utils import success_response
from django.utils.dateparse import parse_datetime
from rest_framework import generics

from .serializers import PrivateSuggestionSerializer
from .tasks import create_suggestion_and_push_notify


class CreateSuggestion(generics.GenericAPIView):
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def post(self, request):
        """Suggest a show to another user."""
        data = json.loads(request.body)
        profile_id = Profile.objects.get(user=request.user).id
        create_suggestion_and_push_notify.delay(data, profile_id)
        return success_response()


class SuggestionList(generics.GenericAPIView):
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def get(self, request):
        """See all suggestions."""
        user = request.user
        suggestions = user.suggestions_received.all()
        suggestion_data = PrivateSuggestionSerializer(suggestions, many=True)
        return success_response(suggestion_data.data)

    def post(self, request):
        """Update the last viewed suggestion time."""
        data = json.loads(request.body)
        suggest_time_viewed = data.get("suggest_time_viewed")
        profile = Profile.objects.get(user=request.user)
        profile.suggest_time_viewed = parse_datetime(suggest_time_viewed)
        profile.save()
        return success_response({"suggest_time_viewed": profile.suggest_time_viewed})
