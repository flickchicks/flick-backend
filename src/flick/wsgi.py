"""
WSGI config for flick project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Uncomment for public server:
# sys.path.append('/var/www/flick-backend/src/flick')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flick.settings")

application = get_wsgi_application()
