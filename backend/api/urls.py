from django.urls import path
from . import views

urlpatterns = [
    # path('register/', views.register, name='register'),
    # path('login/', views.login, name='login'),
    # path('rides/', views.get_rides, name='get_rides'),
    # path('bookings/', views.create_booking, name='create_booking'),
    path('members/', views.members, name='members'),
]
