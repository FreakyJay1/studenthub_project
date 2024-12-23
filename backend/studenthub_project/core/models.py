from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
# Create your models here.

class User(AbstractUser):
    class StudyPreference(models.TextChoices):
        GROUP = "Group", _("Group")
        SOLO = "Solo", _("Solo")

    class Participation(models.TextChoices):
        YES = "Yes", _("Yes")
        NO = "No", _("No")
    
    email = models.EmailField(_("email address"), unique=True)
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)
    favorite_programming_languages = models.CharField(_("favorite programming languages"),max_length=255, blank=True)
    favorite_path = models.JSONField(_("favorite path/focus area"), default=list, blank=True)
    preferred_learning_style = models.JSONField(_("preferred learning style"), default=list, blank=True)
    participate_in_events = models.CharField(_("do you participate in campus events or activities?"),max_length=3, choices=[("Yes","Yes"),("No","No")])
    receive_recommendations = models.CharField(max_length=3, choices=Participation.choices, default=Participation.NO)
    study_preference = models.CharField(_("would you like to receive recommendations for relevant events or activities?"),max_length=3,choices=Participation.choices,default=Participation.NO)
    important_features = models.JSONField(_("which of the following features are most important to you in the dashboard?"),default=list,blank=True,)
    most_used_tool = models.JSONField(_("what is your most used development tool or platform?"), default=list, blank=True)
    recommended_courses = models.JSONField(_("recommended courses"), default=list, blank=True)
    
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
