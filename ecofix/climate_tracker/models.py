from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """
    Extends the default User model to add additional user-related fields.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)  # Points earned by the user

    def __str__(self):
        return self.user.username


class UserActivity(models.Model):
    """
    Stores daily activities of users for carbon footprint tracking.
    """
    TRANSPORTATION_CHOICES = [
        ('car', 'Car'),
        ('bus', 'Bus'),
        ('bike', 'Bike'),
        ('walk', 'Walk'),
        ('train', 'Train'),
    ]

    DIET_CHOICES = [
        ('vegan', 'Vegan'),
        ('vegetarian', 'Vegetarian'),
        ('omnivore', 'Omnivore'),
        ('pescatarian', 'Pescatarian'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transportation = models.CharField(max_length=50, choices=TRANSPORTATION_CHOICES)
    diet = models.CharField(max_length=50, choices=DIET_CHOICES)
    energy_usage = models.FloatField(help_text="Energy usage in kWh/day. Must be between 0 and 100.")
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.date}"
    
class SustainabilityScore(models.Model):
    """
    Stores the sustainability score for each user based on their activities.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    score = models.FloatField(default=0.0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Score: {self.score}"
    
class EnvironmentalObservation(models.Model):
    """
    Stores user-submitted environmental observations.
    """
    OBSERVATION_TYPES = [
        ('air_quality', 'Air Quality'),
        ('water_quality', 'Water Quality'),
        ('noise_pollution', 'Noise Pollution'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    observation_type = models.CharField(max_length=50, choices=OBSERVATION_TYPES)
    description = models.TextField(default="No description provided.")
    location = models.CharField(max_length=255, null=True)  # User-provided location
    latitude = models.FloatField(null=True, blank=True)  # Automatically generated
    longitude = models.FloatField(null=True, blank=True)  # Automatically generated
    timestamp = models.DateTimeField(auto_now_add=True)
    photo = models.ImageField(upload_to='observations/')

    def __str__(self):
        return f"{self.observation_type} by {self.user.username} at {self.location}"
    
