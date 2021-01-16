from datetime import timedelta

from django.conf import settings
from django.utils import timezone
import jwt
import requests


class AppleAuth:
    """apple authentication backend"""

    name = "apple"
    ACCESS_TOKEN_URL = "https://appleid.apple.com/auth/token"
    SCOPE_SEPARATOR = ","
    ID_KEY = "uid"

    def retreive_token(self, access_token):
        """
        Finish the auth process once the access_token was retrieved
        Get the email from ID token received from apple
        """
        response_data = {}
        client_id, client_secret = self.get_key_and_secret()

        headers = {"content-type": "application/x-www-form-urlencoded"}
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": access_token,
            "grant_type": "authorization_code",
        }

        res = requests.post(AppleAuth.ACCESS_TOKEN_URL, data=data, headers=headers)
        response_dict = res.json()
        id_token = response_dict.get("id_token", None)

        if id_token:
            decoded = jwt.decode(id_token, "", verify=False)
            response_data.update({"email": decoded["email"]}) if "email" in decoded else None
            response_data.update({"uid": decoded["sub"]}) if "sub" in decoded else None

        return response_data

    def get_key_and_secret(self):
        headers = {"kid": settings.APPLE_KEY_ID}

        payload = {
            "iss": settings.APPLE_TEAM_ID,
            "iat": timezone.now(),
            "exp": timezone.now() + timedelta(days=180),
            "aud": "https://appleid.apple.com",
            "sub": settings.APPLE_BUNDLE_ID,
        }

        client_secret = jwt.encode(payload, settings.APPLE_PRIVATE_KEY, algorithm="ES256", headers=headers).decode(
            "utf-8"
        )

        return settings.APPLE_BUNDLE_ID, client_secret
