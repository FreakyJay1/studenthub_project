from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
# Create your models here.

class User(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)
    favorite_programming_languages = models.CharField(max_length=255, blank=True)
    favorite_path = models.CharField(max_length=255, blank=True)
    preferred_learning_style = models.CharField(max_length=50, blank=True)
    participate_in_events = models.CharField(max_length=3, choices=[("Yes","Yes"),("No","No")])
    receive_recommendations = models.CharField(max_length=3, choices=[("Yes","Yes"),("No","No")])
    study_preference = models.CharField(max_length=5, choices=[("Group","Group"), ("Solo", "Solo")])
    important_features = models.CharField(max_length=255, blank=True)
    most_used_tool = models.CharField(max_length=255, blank=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        'first_name', 
        'last_name', 
        'favorite_programming_languages',
        'favorite_path',
        'preferred_learning_style',
        'participate_in_events',
        'receive_recommendations',
        'study_preference',
        'important_features',
        'most_used_tool'
    ]
     # Add related_name to avoid reverse accessor clashes
    groups = models.ManyToManyField(
        "auth.Group",
        verbose_name=_("groups"),
        blank=True,
        related_name="custom_user_groups",
        related_query_name="custom_user_group",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        verbose_name=_("user permissions"),
        blank=True,
        related_name="custom_user_permissions",
        related_query_name="custom_user_permission",
    )
    
    def __str__(self):
        return self.email
