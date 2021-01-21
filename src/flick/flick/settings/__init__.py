from decouple import config

is_debug = config("DEBUG")

if is_debug is False:
    from .production import *
else:
    from .local import *
