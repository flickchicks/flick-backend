from datetime import timedelta

from django.conf import settings
from django.utils import timezone
import jwt
import requests


class AppleAuthController:
    """Apple authentication backend"""

    def retreive_token(self, access_token):
        """
        Finish the auth process once the access_token was retrieved
        Get the email from ID token received from apple
        """
        client_id, client_secret = self.get_key_and_secret()

        headers = {"content-type": "application/x-www-form-urlencoded"}
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": access_token,
            "grant_type": "authorization_code",
        }

        res = requests.post(settings.VALIDATE_APPLE_TOKEN_URL, data=data, headers=headers)
        print(res.content)
        response_dict = res.json()
        id_token = response_dict.get("id_token")

        """
        This section is used to retrieve information from the token apple returns, and is temporarily commented out
        """
        # response_data = {}
        # if id_token:
        # decoded = jwt.decode(id_token, "", verify=False, algorithms="")
        # print(f"decoded{decoded}")
        # response_data.update({"email": decoded["email"]}) if "email" in decoded else None
        # response_data.update({"uid": decoded["sub"]}) if "sub" in decoded else None
        return id_token

    def get_key_and_secret(self):
        headers = {"kid": settings.APPLE_KEY_ID}

        payload = {
            "iss": settings.APPLE_TEAM_ID,
            "iat": timezone.now(),
            "exp": timezone.now() + timedelta(days=180),
            "aud": "https://appleid.apple.com",
            "sub": settings.APPLE_BUNDLE_ID,
        }

        client_secret = jwt.encode(payload, settings.APPLE_PRIVATE_KEY, algorithm="ES256", headers=headers)
        return settings.APPLE_BUNDLE_ID, client_secret
