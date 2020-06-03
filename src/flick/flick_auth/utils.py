from django.core import signing
from django.urls import reverse
from django.core.validators import validate_email
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User, Group
from django.conf import settings as django_settings

from rest_framework.authtoken.models import Token

from asset.models import AssetBundle
from user.models import Profile
from . import settings as auth_settings
import re


class AuthTools:
    password_salt = auth_settings.AUTH_PASSWORD_SALT
    token_age = auth_settings.AUTH_TOKEN_AGE

    @staticmethod
    def issue_user_token(user, salt):
        if user is not None:
            if salt == "login":
                token, _ = Token.objects.get_or_create(user=user)
            else:
                token = signing.dumps({"pk": user.pk}, salt=salt)
            return token
        return None

    @staticmethod
    def get_user_from_token(token, salt):
        """
        Verify token for user
        """
        try:
            value = signing.loads(token, salt=AuthTools.password_salt, max_age=900)
        except signing.SignatureExpired:
            return None
        except signing.BadSignature:
            return None

        user = User.objects.get(pk=value["pk"])

        if user is not None:
            return user

        return None

    # good to customize authenticate, can add more interception here
    # ex. sending a notif that someone tried to authenticate, etc
    @staticmethod
    def authenticate(username, social_id_token):
        try:
            # built-in Django authenticate
            user = authenticate(username=username, password=social_id_token)
            if user is not None:
                return user
        except Exception as e:
            print(e)
        return None

    @staticmethod
    def authenticate_email(email, password):
        # check if valid email
        if re.match(r"[^@]+@[^@]+\.[^@]+", email):
            user = AuthTools.get_user_by_email(email)
            if user is not None:
                return AuthTools.authenticate(user.username, password)
        else:
            # otherwise, login as username
            return AuthTools.authenticate(email, password)
        return None

    @staticmethod
    def authenticate_social_id_token(username, social_id_token):
        user = AuthTools.get_user_by_username(username)
        if user is not None:
            return AuthTools.authenticate(user.username, social_id_token)
        return True

    @staticmethod
    def get_user_by_email(email):
        if email:
            try:
                user = User.objects.filter(email=email, is_active=True)[0]
                return user
            except Exception as e:
                print(e)

        return None

    @staticmethod
    def get_user_by_username(username):
        try:
            user = User.objects.filter(username=username, is_active=True)[0]
            return user
        except Exception as e:
            print(e)
        return None

    @staticmethod
    def login(request, user):
        if user is not None:
            try:
                login(request, user)
                return True
            except Exception as e:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(e).__name__, e.args)
                print(message)
        return False

    @staticmethod
    def logout(request):
        if request:
            try:
                Token.objects.filter(user=request.user).delete()
                logout(request)
                return True
            except Exception as e:
                print(e)
                pass
        return False

    @staticmethod
    def register(user_data, profile_data, group):
        """
        Register user:
            user_data = {'username', 'first_name', 'last_name'}
            profile_data = {'profile_pic', 'social_id_token', 'social_id_token_type'}
        """
        try:
            username_exists = User.objects.filter(username=user_data["username"])
            if username_exists:
                return {"user": username_exists[0], "is_new": False}

            user = User.objects.create_user(**user_data)

            profile_data["user"] = user
            profile = Profile(**profile_data)
            profile.save()

            group = Group.objects.get(name=group)
            group.user_set.add(user)

            return {"user": user, "is_new": True}
        except Exception as e:
            print(str(e))
            raise Exception(e)
        return None

    @staticmethod
    def profile_register(user, profile_data):
        """
        Register user profile:
            profile_data = {'role', 'position'}
        """
        try:
            return Profile.objects.get(pk=user.id)
        except ObjectDoesNotExist:
            try:
                profile_data["user"] = user
                profile = Profile(**profile_data)
                profile.save()

                group = Group.objects.get(name=profile_data["role"] + "_basic")
                group.user_set.add(user)

                return profile
            except Exception as e:
                print(e)
        return None

    @staticmethod
    def set_password(user, password, new_password):
        """
        Set user's password
        """
        if user.has_usable_password():
            if user.check_password(password) and password != new_password:
                user.set_password(new_password)
                user.save()
                return True
        elif new_password:
            user.set_password(new_password)
            user.save()
            return True
        return False

    @staticmethod
    def reset_password(token, new_password):
        """
        Reset user's forgotten password
        """
        user = AuthTools.get_user_from_token(token, AuthTools.password_salt)
        if user is not None:
            user.set_password(new_password)
            user.save()
            return user
        return None

    @staticmethod
    def validate_username(username):
        """
        Validate that the username is formatted and unique
        """
        min_username_length = 3
        stats = "valid"
        if len(username) < min_username_length:
            stats = "invalid"
        elif re.match("^[a-zA-Z0-9_-]+$", username) is None:
            stats = "invalid"
        else:
            user = AuthTools.get_user_by_username(username)
            if user is not None:
                stats = "taken"
        return stats

    @staticmethod
    def validate_email(email):
        """
        Validate the email is formatted and unique
        """
        status = "valid"
        try:
            validate_email(email)
            user = AuthTools.get_user_by_email(email)
            if user is not None:
                status = "taken"
        except Exception as e:
            print(e)
            status = "invalid"
        return status

    @staticmethod
    def validate_password(password):
        min_password_length = 7
        is_valid = True
        if len(password) < min_password_length:
            is_valid = False
        return is_valid
