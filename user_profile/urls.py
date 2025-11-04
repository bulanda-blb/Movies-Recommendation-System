from django.urls import path
from . import views


urlpatterns = [
    path('watchlist/', views.watchlist, name="watchlist"),
    path('edit_profile/', views.edit_profile, name="edit_profile"),
    path('history/', views.history, name="history"),
    path('history/delete/', views.delete_history, name='delete_history'),
    path('recommendations/', views.recommendations, name='recommendations'),
    path('preferences/', views.preferences, name="preferences"),
    path('logout/', views.logout, name="logout"),
]

