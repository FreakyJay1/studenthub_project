from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    favorite_path = forms.MultipleChoiceField(
        choices=[
            ('Mobile Development', 'Mobile Development'),
            ('Blockchain', 'Blockchain'),
            ('Web Development', 'Web Development'),
            ('Data Science', 'Data Science')
        ],
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    preferred_learning_style = forms.MultipleChoiceField(
        choices=[
            ('Visual', 'Visual'),
            ('Auditory', 'Auditory'),
            ('Kinesthetic', 'Kinesthetic')
        ],
        widget=forms.CheckboxSelectMultiple,
        required=True
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
        required=True
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