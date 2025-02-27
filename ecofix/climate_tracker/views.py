import googlemaps
import json
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.contrib import messages
from django.core.paginator import Paginator
from .forms import CustomUserCreationForm, UserActivityForm, GreenActionSimulatorForm, ObservationForm, CustomAuthenticationForm
from .utils import calculate_carbon_footprint, calculate_sustainability_score, format_chart_data, generate_chat_response
from .models import UserActivity, UserProfile, SustainabilityScore, EnvironmentalObservation, ShopItem, Purchase
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

# Registration View
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after registration
            return redirect('home')  # Redirect to homepage
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

# Login View
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to homepage
        else:
            error_message = "Invalid username or password."
            return render(request, 'login.html', {'error_message': error_message})
    return render(request, 'login.html')

# Home View (Protected by @login_required)
@login_required
def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'home.html')

# Carbon Footprint Tracker View
@login_required
def track_carbon_footprint(request):
    if request.method == 'POST':
        form = UserActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.user = request.user
            activity.save()

            # Prepare user input for carbon footprint calculation
            user_input = f"Transportation: {activity.transportation}, Diet: {activity.diet}, Energy Usage: {activity.energy_usage} kWh/day"

            try:
                # Calculate and parse the carbon footprint
                footprint = calculate_carbon_footprint(user_input)
            except ValueError as e:
                return render(request, 'error.html', {'message': str(e)})

            # Pass the parsed carbon footprint to the template
            return render(request, 'carbon_result.html', {'footprint': footprint})
    else:
        form = UserActivityForm()
    return render(request, 'track_carbon.html', {'form': form})

@login_required
def calculate_sustainability(request):
    """
    View to calculate the user's latest sustainability score and provide historical trends.
    """
    # Fetch all activities for the logged-in user, ordered by date (newest first)
    user_activities = UserActivity.objects.filter(user=request.user).order_by('-date')

    # Initialize default values
    latest_result = {'score': None, 'breakdown': [], 'suggestions': []}
    chart_data = "[]"

    # Calculate the latest sustainability score
    if user_activities.exists():
        latest_activity = user_activities.first()  # Get the most recent activity
        latest_result = calculate_sustainability_score([latest_activity])

        # Format historical data for the chart
        chart_data = format_chart_data(user_activities)

    return render(request, 'sustainability_score.html', {
        'latest_result': latest_result,
        'chart_data': chart_data
    })


@login_required
def submit_observation(request):
    if request.method == 'POST':
        form = ObservationForm(request.POST, request.FILES)
        if form.is_valid():
            # Get the location from the form
            location = form.cleaned_data['location']

            # Use Google Maps Geocoding API to get latitude and longitude
            geocode_result = gmaps.geocode(location)
            if not geocode_result:
                return render(request, 'error.html', {'message': 'Invalid location. Please enter a valid address.'})

            # Extract latitude and longitude
            latitude = geocode_result[0]['geometry']['location']['lat']
            longitude = geocode_result[0]['geometry']['location']['lng']

            # Save the observation
            observation = form.save(commit=False)
            observation.user = request.user
            observation.latitude = latitude
            observation.longitude = longitude
            observation.save()

            # Increment user points
            user_profile, created = UserProfile.objects.get_or_create(user=request.user)
            user_profile.points += 1  # Add 1 point per submission
            user_profile.save()

            return redirect('map_view')
    else:
        form = ObservationForm()
    return render(request, 'submit_observation.html', {'form': form})

@login_required
def map_view(request):
    observations = EnvironmentalObservation.objects.all()
    # Serialize observations to JSON
    observations_json = serialize('json', observations, fields=('latitude', 'longitude', 'observation_type'))
    return render(request, 'map.html', {'observations': observations_json})

@login_required
def all_observations(request):
    """
    Displays a paginated list of all environmental observations submitted by users.
    Supports filtering by observation type.
    """
    # Fetch all observations
    observations = EnvironmentalObservation.objects.all().order_by('-timestamp')

    # Optional: Filter by observation type
    observation_type = request.GET.get('type', None)
    if observation_type:
        observations = observations.filter(observation_type=observation_type)

    # Paginate the results (10 observations per page)
    paginator = Paginator(observations, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'all_observations.html', {'page_obj': page_obj})

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def chatbot(request):
    if request.method == 'POST':
        # Handle POST requests for chatbot responses
        user_message = request.POST.get('message', '').strip()

        if not user_message:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)

        try:
            bot_response = generate_chat_response(user_message)
            return JsonResponse({'response': bot_response})
        except Exception as e:
            logger.error(f"Error in chatbot view: {str(e)}")
            return JsonResponse({'error': 'An error occurred while processing your request. Please try again later.'}, status=500)

    elif request.method == 'GET':
        # Render the chat interface for GET requests
        return render(request, 'chatbot.html')

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def shopnow(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    items = ShopItem.objects.all()
    
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        try:
            item = ShopItem.objects.get(id=item_id)
            
            if user_profile.points >= item.points_cost:
                # Deduct points
                user_profile.points -= item.points_cost
                user_profile.save()
                
                message = f"Successfully redeemed {item.name}!"
            else:
                message = "Not enough points to redeem this item."
        except ShopItem.DoesNotExist:
            message = "Item not found."

        return render(request, 'shopnow.html', {'items': items, 'user_points': user_profile.points, 'message': message})
    
    return render(request, 'shopnow.html', {'items': items, 'user_points': user_profile.points})

@login_required
def checkout(request, purchase_id):
    try:
        purchase = Purchase.objects.get(id=purchase_id, user=request.user)
    except Purchase.DoesNotExist:
        return redirect('shopnow')  # If purchase not found, go back to shop

    return render(request, 'checkout.html', {'purchase': purchase})