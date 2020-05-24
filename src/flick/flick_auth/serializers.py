from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.authtoken.models import Token 

from user.serializers import ProfileSerializer, UserSerializer
from .utils import AuthTools

User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    
    email = serializers.EmailField()

    class Meta:
        model = User
        # Django's REQUIRED_FIELDS
        fields = tuple(User.REQUIRED_FIELDS) + (
            User.USERNAME_FIELD,
            'email',
            'first_name',
            'last_name',
            'password',
        )
        write_only_fields = (
            'email',
            'first_name',
            'last_name',
            'password',
        )
    
    def save(self, **kwargs):
        data = self.init_data if hasattr(self, 'init_data') else self.initial_data

        items = dict(data.items())
        user_data = {
            'username': items['username'],
            'email': items['email'],
            'password': items['password'],
        }

        profile_data = {
            'role': 'consumer',
        }

        group = profile_data['role'] + '_basic'
        user = AuthTools.register(user_data, profile_data, group)

        if user is not None:
            self.object = user
            return self.object 

        raise serializers.ValidationError('Unable to register with the credentials provided.')

class LoginSerializer(serializers.ModelSerializer):
    auth_token = serializers.CharField(source='key')
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Token 
        fields = (
            'auth_token',
            'user'
        )
        read_only_fields = fields

