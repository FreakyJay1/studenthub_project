from django.contrib.auth.backends import ModelBackend
from .db import get_user_by_email
from django.contrib.auth import get_user_model

class EmailBackend(ModelBackend):
    def authenticate(self, request, username = None, password = None, **kwargs):
        User = get_user_model
        try:
            user_doc = get_user_by_email(username)
            if user_doc:
                django_user = User.objects.get(email=user_doc['email'])
                if django_user.check_password(password):
                    return django_user
        except User.DoesNotExist:
            return None
        except Exception as e:
            print(f"An error occurred during authentication: {e}")
            return None

        return None