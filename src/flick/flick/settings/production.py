from decouple import config

DEBUG = False
PRODUCTION = True
SECRET_KEY = config("SECRET_KEY")
VALIDATE_SOCIAL_TOKEN = True
