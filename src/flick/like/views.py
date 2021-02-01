from user.models import Profile

from api import settings as api_settings
from api.utils import failure_response
from api.utils import success_response
from comment.models import Comment
from comment.serializers import CommentSerializer
from lst.models import Lst
from lst.serializers import LstWithSimpleShowsSerializer
from notification.models import Notification
from rest_framework import generics

from .models import Like


class LikeView(generics.GenericAPIView):
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def _create_comment_like_notification(self, from_user, to_user, comment):
        from_profile = Profile.objects.get(user=from_user)
        notif = Notification()
        notif.notif_type = "comment_like"
        notif.from_user = from_profile
        notif.to_user = to_user
        notif.comment = comment
        notif.save()

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
            like = Like()
            like.comment = comment
            like.type = "comment_like"
            like.liker = profile
            like.save()
        else:
            comment.num_likes -= 1
            existing_like.delete()

        comment.save(update_fields=["num_likes"])
        if request.user.id != comment.owner.user.id:
            self._create_comment_like_notification(user, comment.owner, comment)
        comment_data = CommentSerializer(comment, context={"request": request}).data
        return success_response(comment_data)


class LstLikeView(generics.GenericAPIView):
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def _create_lst_like_notification(self, from_user, to_user, lst):
        from_profile = Profile.objects.get(user=from_user)
        notif = Notification()
        notif.notif_type = "list_like"
        notif.from_user = from_profile
        notif.to_user = to_user
        notif.lst = lst
        notif.save()

    def _create_like(self, lst, liker_profile):
        like = Like()
        like.lst = lst
        like.type = "list_like"
        like.liker = liker_profile
        like.save()

    def post(self, request, pk):
        if not Lst.objects.filter(id=pk).exists():
            return failure_response(f"List of id {pk} does not exist.")
        lst = Lst.objects.get(pk=pk)
        user = request.user
        if not Profile.objects.filter(user=user).exists():
            return failure_response(f"{user} must be logged in.")
        profile = Profile.objects.get(user=user)
        existing_like = lst.likers.filter(liker=profile)
        if not existing_like:
            lst.num_likes += 1
            self._create_like(lst, profile)
            if request.user.id != lst.owner.user.id:
                self._create_lst_like_notification(user, lst.owner, lst)
        else:
            lst.num_likes -= 1
            existing_like.delete()

        lst.save(update_fields=["num_likes"])
        lst_data = LstWithSimpleShowsSerializer(lst, context={"request": request}).data
        return success_response(lst_data)
