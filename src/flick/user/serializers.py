from django.contrib.auth.models import User

from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField

from user.models import Profile

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 
            'username',
            'email',
        )
        read_only_fields = ('id',)

class ProfileSerializer(ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            'id', 
            'bio',
            'phone_number',
        )
        read_only_fields = ('id',)