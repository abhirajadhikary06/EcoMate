from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

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
    energy_usage = models.FloatField(help_text="Energy usage in kWh/day. Must be between 0 and 100.", default=0)
    date = models.DateField(auto_now_add=True)
    distance_travelled = models.FloatField(help_text="Distance travelled in kms.", default=0)

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
    
class ShopItem(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    points_cost = models.IntegerField()
    image = models.ImageField(upload_to='items/', blank=True, null=True)  # For local images
    image_url = models.URLField(blank=True, null=True)  # For external images

    def get_image(self):
        """Return the image URL, prioritizing the local image if available."""
        if self.image:
            return self.image.url
        return self.image_url

    def __str__(self):
        return self.name

class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(ShopItem, on_delete=models.CASCADE)
    date_purchased = models.DateTimeField(auto_now_add=True)
    delivery_address = models.TextField(blank=True, null=True)  # Address for delivery

    def __str__(self):
        return f"{self.user.username} purchased {self.item.name}"
