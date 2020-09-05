from user.models import Profile

from api import settings as api_settings
from api.utils import failure_response
from api.utils import success_response
from comment.models import Comment
from comment.serializers import CommentSerializer
from rest_framework import generics


class ReadView(generics.GenericAPIView):
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def post(self, request, pk):
        if not Comment.objects.filter(pk=pk):
            return failure_response(f"Comment of id {pk} does not exist.")
        comment = Comment.objects.get(pk=pk)
        if not comment.is_spoiler:
            return failure_response(f"Comment {pk} is not a spoiler.")

        user = request.user
        if not Profile.objects.filter(user=user):
            return failure_response(f"{user} must be logged in.")
        profile = Profile.objects.get(user=user)

        if not comment.reads.filter(reader=profile):
            comment.reads.create(reader=profile)

        comment_data = CommentSerializer(comment, context={"request": request}).data
        return success_response(comment_data)
