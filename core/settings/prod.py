#import os


from .base import *
print(888888888888888888888888888888)
# DEBUG = False
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'jerrychinedu.pythonanywhere.com']

print(9999999999999999999999999999999999999)
# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "jerrychinedu$default",
        "USER": "jerrychinedu",
        "PASSWORD": "Kseniapeguy@gm3il",
        "HOST": "jerrychinedu.mysql.pythonanywhere-services.com",
        
    }
}

