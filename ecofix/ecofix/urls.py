from django.urls import path, reverse_lazy
from climate_tracker import views
from django.conf import settings
from django.conf.urls.static import static

# urls.py

from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('', views.landing, name='landing'),
    path('register/', views.register, name='register'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('home/', views.home, name='home'),  # Moved 'home' to '/home/'
    path('track-carbon/', views.track_carbon_footprint, name='track_carbon'),
    path('sustainability-score/', views.calculate_sustainability, name='calculate_sustainability'),
    path('submit-observation/', views.submit_observation, name='submit_observation'),
    path('map-view/', views.map_view, name='map_view'),
    path('all-observations/', views.all_observations, name='all_observations'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('shopnow/', views.shopnow, name='shopnow'),
    path('checkout/<int:purchase_id>/', views.checkout, name='checkout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)