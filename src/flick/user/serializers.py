from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField

from django.contrib.auth.models import User

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 
            'username',
            'email',
        )
        read_only_fields = ('id',)