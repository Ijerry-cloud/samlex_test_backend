"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from dotenv import find_dotenv, load_dotenv

try:
    load_dotenv(find_dotenv(filename="env/local.env", raise_error_if_not_found=True))
except OSError:
    load_dotenv(find_dotenv(filename="env/prod.env"))

application = get_asgi_application()
