from django.contrib import admin
from .models import Watchlist, SearchHistory

@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display   = ('user', 'movie', 'added_at')
    list_filter    = ('added_at', 'user')
    search_fields  = ('user__email', 'movie__title')
    raw_id_fields  = ('user', 'movie')
    ordering       = ('-added_at',)

@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'query',
        'timestamp',
    )
    list_filter = (
        'timestamp',
    )
    search_fields = (
        'query',
        'user__email',
    )
    readonly_fields = (
        'timestamp',
        'top_results',
    )
    ordering = ('-timestamp',)
    fieldsets = (
        (None, {
            'fields': ('user', 'query', 'top_results')
        }),
        ('Timestamps', {
            'fields': ('timestamp',),
        }),
    )