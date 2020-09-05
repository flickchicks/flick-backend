from user.models import Profile

from api import settings as api_settings
from api.utils import failure_response
from api.utils import success_response
from comment.models import Comment
from comment.serializers import CommentSerializer
from rest_framework import generics


class LikeView(generics.GenericAPIView):
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def post(self, request, pk):
        if not Comment.objects.filter(pk=pk):
            return failure_response(f"Comment of id {pk} does not exist.")
        comment = Comment.objects.get(pk=pk)

        user = request.user
        if not Profile.objects.filter(user=user):
            return failure_response(f"{user} must be logged in.")
        profile = Profile.objects.get(user=user)

        existing_like = comment.likers.filter(liker=profile)
        if not existing_like:
            comment.num_likes += 1
            comment.likers.create(liker=profile)
        else:
            comment.num_likes -= 1
            existing_like.delete()

        comment.save(update_fields=["num_likes"])

        comment_data = CommentSerializer(comment, context={"request": request}).data
        return success_response(comment_data)
