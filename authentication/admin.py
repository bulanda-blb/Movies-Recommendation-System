from django.contrib import admin
from authentication.models import movie_user
from .models import Preference

class PreferenceInline(admin.StackedInline):
    model = Preference
    extra = 0
    fieldsets = (
        (None, {
            'fields': (
                'genres',
                'moods',
                'preferred_length',
                'context',
                'frequency',
                'subtitles',
                'era',
                'content_type',
            ),
        }),
    )
    readonly_fields = ()

@admin.register(movie_user)
class MovieUserAdmin(admin.ModelAdmin):
    list_display = (
        'user_id',
        'email',
        'is_active',
        'notification_on',
        'join_time',
    )
    list_filter = (
        'is_active',
        'notification_on',
    )
    search_fields = ('email',)
    inlines = [PreferenceInline]

@admin.register(Preference)
class PreferenceAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'preferred_length',
        'context',
        'frequency',
        'subtitles',
    )
    list_filter = (
        'preferred_length',
        'context',
        'frequency',
        'subtitles',
    )
    search_fields = ('user__email', 'user__user_id')
    readonly_fields = ()
    fieldsets = (
        (None, {
            'fields': (
                'user',
                'genres',
                'moods',
                'preferred_length',
                'context',
                'frequency',
                'subtitles',
                'era',
                'content_type',
            ),
        }),
    )
