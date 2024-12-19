from django.contrib.auth.backends import ModelBackend
from .db import get_user_by_email
from django.contrib.auth import get_user_model

class EmailBackend(ModelBackend):
    def authenticate(self, request, username = None, password = None, **kwargs):
        user = get_user_model
        user = get_user_by_email(username)
        if user is not None:
            django_user = user.objects.filter(email=username).first()
            if django_user and django_user.check_password(password):
                return django_user
        
        return None