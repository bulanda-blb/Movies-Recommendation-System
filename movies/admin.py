# movies/admin.py

from django.contrib import admin
from .models import RawMovie


@admin.register(RawMovie)
class RawMovieAdmin(admin.ModelAdmin):
    list_display   = (
        'tmdb_id',
        'title',
        'release_date',
        'vote_average',
        'popularity',
    )
    list_filter    = ('release_date', 'adult')
    search_fields  = ('title', 'overview', 'genres', 'keywords')
    ordering       = ('-popularity',)
    list_per_page  = 50
