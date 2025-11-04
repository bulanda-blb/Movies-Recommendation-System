from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('explore/', views.explore, name='explore'),
    path('watchlist/toggle/', views.toggle_watchlist, name='toggle_watchlist'),
    path('search/',     views.search,  name='search'),
    path('movie/<int:tmdb_id>/', views.movie_detail, name='movie_detail'),
    path('ajax/toggle-watchlist/', views.toggle_watchlist_ajax, name='toggle_watchlist_ajax'),

]
