import os

ALLOWED_HOSTS = ["app"]
DEBUG = False
PRODUCTION = True
SECRET_KEY = os.environ.get("SECRET_KEY")
VALIDATE_SOCIAL_TOKEN = True
