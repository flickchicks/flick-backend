from user.models import Profile
from user.profile_simple_serializers import ProfileSimpleSerializer

from like.serializers import LikeSerializer
from rest_framework import serializers
from show.serializers import ShowSearchSerializer
from show.simple_serializers import ShowSimplestSerializer
from tag.simple_serializers import TagSimpleSerializer

from .models import Lst
from .models import LstSaveActivity


class LstSerializer(serializers.ModelSerializer):
    collaborators = ProfileSimpleSerializer(many=True)
    owner = ProfileSimpleSerializer(many=False)
    shows = ShowSearchSerializer(many=True)
    tags = TagSimpleSerializer(many=True)
    likers = LikeSerializer(many=True)
    has_liked = serializers.SerializerMethodField(method_name="get_has_liked")

    def get_has_liked(self, lst):
        request = self.context.get("request")
        user = request.user

        if not Profile.objects.filter(user=user):
            return False
        profile = Profile.objects.get(user=user)

        has_liked = lst.likers.filter(liker=profile).exists()
        return has_liked

    class Meta:
        model = Lst
        fields = (
            "id",
            "name",
            "pic",
            "description",
            "is_saved",
            "is_private",
            "is_watch_later",
            "collaborators",
            "owner",
            "shows",
            "tags",
            "has_liked",
            "num_likes",
            "likers",
        )
        read_only_fields = fields


class LstWithSimpleShowsSerializer(serializers.ModelSerializer):
    collaborators = ProfileSimpleSerializer(many=True)
    owner = ProfileSimpleSerializer(many=False)
    shows = ShowSimplestSerializer(many=True)
    tags = TagSimpleSerializer(many=True)
    likers = LikeSerializer(many=True)
    has_liked = serializers.SerializerMethodField(method_name="get_has_liked")

    def get_has_liked(self, lst):
        request = self.context.get("request")
        if not request:
            return False
        user = request.user
        if not Profile.objects.filter(user=user):
            return False
        profile = Profile.objects.get(user=user)
        has_liked = lst.likers.filter(liker=profile).exists()
        return has_liked

    class Meta:
        model = Lst
        fields = (
            "id",
            "name",
            "pic",
            "description",
            "is_saved",
            "is_private",
            "is_watch_later",
            "collaborators",
            "owner",
            "shows",
            "tags",
            "num_likes",
            "has_liked",
            "likers",
        )
        read_only_fields = fields


class LstSaveActivitySerializer(serializers.ModelSerializer):
    saved_by = ProfileSimpleSerializer(many=False)
    lst_name = serializers.SerializerMethodField(method_name="get_lst_name")
    lst_id = serializers.SerializerMethodField(method_name="get_lst_id")

    class Meta:
        model = LstSaveActivity
        fields = ("lst_id", "lst_name", "saved_by")

    def get_lst_name(self, instance):
        return instance.lst.name

    def get_lst_id(self, instance):
        return instance.lst.id
