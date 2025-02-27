from django.urls import path, reverse_lazy
from climate_tracker import views

# urls.py

from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('', views.home, name='home'),
    path('track-carbon/', views.track_carbon_footprint, name='track_carbon'),
    path('sustainability-score/', views.calculate_sustainability, name='calculate_sustainability'),
    path('submit-observation/', views.submit_observation, name='submit_observation'),
    path('map-view/', views.map_view, name='map_view'),
    path('all-observations/', views.all_observations, name='all_observations'),
    path('chatbot/', views.chatbot, name='chatbot'),
]