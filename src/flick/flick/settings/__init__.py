from decouple import config

DEBUG = config("DEBUG", default=False, cast=bool)

if DEBUG is False:
    from .production import *
else:
    from .local import *
