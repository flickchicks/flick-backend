import json
from user.models import Profile
from user.serializers import ProfileSerializer
from user.serializers import UserProfileSerializer

from api import settings as api_settings
from api.utils import failure_response
from api.utils import success_response
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.db.models import Prefetch
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from like.models import Like
from lst.simple_serializers import MeLstSerializer
from rest_framework import generics
from rest_framework.authtoken.models import Token

from .controllers.authenticate_controller import AuthenticateController
from .controllers.check_username_controller import CheckUsernameController
from .controllers.update_profile_controller import UpdateProfileController
from .serializers import AuthenticateSerializer
from .serializers import LogoutSerializer


class UserView(generics.GenericAPIView):
    model = Profile
    serializer_class = ProfileSerializer
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def delete(self, request):
        try:
            request.user.delete()
        except Exception as e:
            return failure_response(f"An exception occurred {e}.")
        return success_response(f"User with id {request.user.id} has been deleted.")

    def get(self, request):
        profile = Profile.objects.filter(user=self.request.user).prefetch_related(
            "owner_lsts",
            "collab_lsts",
            "owner_lsts__owner",
            "owner_lsts__collaborators",
            "owner_lsts__shows",
            "collab_lsts__owner",
            "collab_lsts__collaborators",
            "collab_lsts__shows",
        )[0]
        serializer = self.serializer_class(profile)
        return success_response(serializer.data)

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = request.data
        return UpdateProfileController(request, data, self.serializer_class).process()


class CheckUsernameView(generics.GenericAPIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = request.data
        return CheckUsernameController(request, data).process()


class UserProfileView(generics.GenericAPIView):
    model = Profile
    serializer_class = UserProfileSerializer
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def get(self, request, pk):
        if request.user.id == pk:
            return HttpResponseRedirect(reverse("me"))
        if not User.objects.filter(id=pk):
            return failure_response(f"User of id {pk} not found.")
        profile = Profile.objects.filter(user__id=pk).prefetch_related(
            "owner_lsts",
            "collab_lsts",
            "owner_lsts__owner",
            "owner_lsts__collaborators",
            "owner_lsts__shows",
            "collab_lsts__owner",
            "collab_lsts__collaborators",
            "collab_lsts__shows",
        )[0]
        return success_response(self.serializer_class(profile, context={"request": self.request}).data)


class UserLikedLstsView(generics.GenericAPIView):
    model = Profile
    serializer_class = MeLstSerializer
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def get(self, request, pk):
        if not User.objects.filter(id=pk):
            return failure_response(f"User of id {pk} not found.")
        profile = (
            Profile.objects.filter(user__id=pk)
            .prefetch_related(
                Prefetch("likes", queryset=Like.objects.filter(like_type="list_like", to_attr="lst_likes"))
            )
            .get()
        )
        lsts = profile.lst_likes.values_list("lst", flat=True)

        # someAlbums = PhotoAlbum.objects.filter(author="Davey Jones").prefetch_related(
        #     Prefetch(ßß
        #         "photo_set",
        #         queryset=Photo.objects.filter(format=1),
        #         to_attr="some_photos"
        #     )
        # )

        # for a in someAlbums:
        #     somePhotos = a.some_photos

        return success_response(self.serializer_class(lsts, many=True, context={"request": self.request}).data)


class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = api_settings.CONSUMER_PERMISSIONS

    def logout(self, request):
        if request:
            try:
                Token.objects.filter(user=request.user).delete()
                logout(request)
                return True
            except Exception as e:
                print(e)
                pass
        return False

    def post(self, request):
        if self.logout(request):
            return success_response(None)
        return failure_response(None)


class AuthenticateView(generics.GenericAPIView):
    serializer_class = AuthenticateSerializer
    permission_classes = api_settings.UNPROTECTED

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = request.data
        return AuthenticateController(request, data, self.serializer_class).process()
