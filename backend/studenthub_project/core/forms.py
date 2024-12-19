from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email Address")
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    favorite_programming_languages = forms.CharField(
        required=False, widget=forms.TextInput(attrs={'placeholder': 'e.g., Python, JavaScript'})
    )
    favorite_path = forms.MultipleChoiceField(
        choices=[
            ('Mobile Development', 'Mobile Development'),
            ('Blockchain', 'Blockchain'),
            ('Web Development', 'Web Development'),
            ('Data Science', 'Data Science')
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    preferred_learning_style = forms.MultipleChoiceField(
        choices=[
            ('Visual', 'Visual'),
            ('Auditory', 'Auditory'),
            ('Kinesthetic', 'Kinesthetic')
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    participate_in_events = forms.ChoiceField(
        choices=User.Participation.choices,
        widget=forms.RadioSelect,
        required=True,
        label="Do you participate in campus events or activities?",
        initial=User.Participation.NO
    )
    receive_recommendations = forms.ChoiceField(
        choices=User.Participation.choices,
        widget=forms.RadioSelect,
        required=True,
        label="Would you like to receive recommendations for relevant events or activities?",
        initial=User.Participation.NO
    )
    study_preference = forms.ChoiceField(
        choices=User.StudyPreference.choices,
        widget=forms.RadioSelect,
        required=True,
        label="Do you prefer group study or solo study?",
        initial=User.StudyPreference.SOLO
    )
    important_features = forms.MultipleChoiceField(
        choices=[
            ('Upcoming deadlines', 'Upcoming deadlines'),
            ('Course materials', 'Course materials'),
            ('Study groups', 'Study groups'),
            ('Event recommendations', 'Event recommendations'),
            ('Campus resources', 'Campus resources'),
            ('Messages', 'Messages')
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    most_used_tool = forms.MultipleChoiceField(
        choices=[
            ('VS Code', 'VS Code'),
            ('IntelliJ IDEA', 'IntelliJ IDEA'),
            ('GitHub', 'GitHub'),
            ('Jupyter Notebooks', 'Jupyter Notebooks'),
            ('Pycharm', 'Pycharm')
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + (
            'email',
            'first_name',
            'last_name',
            'favorite_programming_languages',
            'favorite_path',
            'preferred_learning_style',
            'participate_in_events',
            'receive_recommendations',
            'study_preference',
            'important_features',
            'most_used_tool',
        )
    # To check if that email is already use in the database.
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already use in the database.")
        return email