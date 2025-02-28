from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserActivity, EnvironmentalObservation, UserProfile, SustainabilityScore
class CustomUserCreationForm(UserCreationForm):
    """
    Custom form for user registration, including an email field.
    """
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserActivityForm(forms.ModelForm):
    """
    Form for users to input their daily activities (transportation, diet, energy usage).
    """
    class Meta:
        model = UserActivity
        fields = ['transportation', 'diet', 'energy_usage', 'distance_travelled']

    def clean_energy_usage(self):
        """
        Validate the energy_usage field to ensure it is within a realistic range.
        """
        energy_usage = self.cleaned_data.get('energy_usage')
        if energy_usage < 0:
            raise forms.ValidationError("Energy usage cannot be negative.")
        if energy_usage > 100:
            raise forms.ValidationError("Energy usage cannot exceed 100 kWh/day.")
        return energy_usage


class CustomAuthenticationForm(AuthenticationForm):
    """
    Custom authentication form (extends Django's default AuthenticationForm).
    """
    pass  # Use Django's default AuthenticationForm without modifications

class GreenActionSimulatorForm(forms.Form):
    action = forms.ChoiceField(
        choices=[
            ('switch_to_renewable_energy', 'Switch to Renewable Energy'),
            ('reduce_meat_consumption', 'Reduce Meat Consumption'),
            ('use_public_transport', 'Use Public Transport'),
        ],
        widget=forms.RadioSelect,
        label="Select an Action"
    )


class ObservationForm(forms.ModelForm):
    class Meta:
        model = EnvironmentalObservation
        fields = ['observation_type', 'description', 'location', 'photo']
        widgets = {
            'location': forms.TextInput(attrs={'placeholder': 'Enter location or use current location'}),
        }