from decouple import config

ALLOWED_HOSTS = ["app"]
DEBUG = False
PRODUCTION = True
SECRET_KEY = config("SECRET_KEY")
VALIDATE_SOCIAL_TOKEN = True
