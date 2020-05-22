from django.contrib.auth.models import User

from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 
            'username',
            'email',
        )
        read_only_fields = ('id',)