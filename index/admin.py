

from django.contrib import admin
from .models import GenreRecommendation
from .models import PrecomputedPool
from .models import GenreMovieSearch

@admin.register(GenreRecommendation)
class GenreRecommendationAdmin(admin.ModelAdmin):
    list_display = ('genre', 'movie_count', 'updated_at')
    readonly_fields = ('updated_at',)
    fields = ('genre', 'movie_ids', 'updated_at')
    ordering = ('genre',)

    def movie_count(self, obj):
        # show how many IDs are stored
        return len(obj.movie_ids)
    movie_count.short_description = 'Number of Movies'




@admin.register(PrecomputedPool)
class PrecomputedPoolAdmin(admin.ModelAdmin):
    list_display  = ('key', 'movie_count', 'updated_at')
    readonly_fields = ('updated_at',)
    fields        = ('key', 'movie_ids', 'updated_at')
    ordering      = ('key',)

    def movie_count(self, obj):
        return len(obj.movie_ids)
    movie_count.short_description = 'Number of Movies'




# from .models import GenreMovieSearch

# @admin.register(GenreMovieSearch)
# class GenreMovieSearchAdmin(admin.ModelAdmin):
#     list_display = ('id', 'movie_id', 'title')
#     search_fields = ('title', 'normalized_title', 'keywords', 'overview')
#     list_filter = ()


# from .models import Genre, GenreMovieMap

# @admin.register(Genre)
# class GenreAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name')
#     search_fields = ('name',)
#     ordering = ('name',)

# @admin.register(GenreMovieMap)
# class GenreMovieMapAdmin(admin.ModelAdmin):
#     list_display = ('id', 'genre', 'movie_id')
#     list_filter = ('genre',)
#     search_fields = ('movie_id',)
#     ordering = ('genre', 'movie_id')


from .models import GenreMovies

@admin.register(GenreMovies)
class GenreMoviesAdmin(admin.ModelAdmin):
    list_display = ('genre', 'num_movies')
    search_fields = ('genre',)

    def num_movies(self, obj):
        return len(obj.movie_ids)
    num_movies.short_description = 'Number of Movies'
