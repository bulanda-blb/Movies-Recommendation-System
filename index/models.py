from django.db import models

class GenreRecommendation(models.Model):
    genre       = models.CharField(max_length=64, unique=True)
    movie_ids   = models.JSONField(
        help_text="Ordered list of top tmdb_id for this genre"
    )
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.genre} ({len(self.movie_ids)} movies)"




class PrecomputedPool(models.Model):
    """
    Stores precomputed ordered tmdb_id lists for:
      - each category (key="category_<name>")
      - each genre    (key="genre_<name>")
    """
    key        = models.CharField(max_length=64, unique=True)
    movie_ids  = models.JSONField(
        help_text="Ordered list of tmdb_id for this key"
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.key} ({len(self.movie_ids)} movies)"




class GenreMovieSearch(models.Model):
    id = models.AutoField(primary_key=True)
    movie_id = models.IntegerField(db_index=True)    # RawMovie.tmdb_id
    title = models.CharField(max_length=255, db_index=True)
    normalized_title = models.CharField(max_length=255, db_index=True)
    keywords = models.TextField(blank=True)
    overview = models.TextField(blank=True)

    class Meta:
        db_table = "movie_search"
        indexes = [
            models.Index(fields=['normalized_title']),
            models.Index(fields=['title']),
        ]

    def __str__(self):
        return f"{self.movie_id} - {self.title}"


class Genre(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, db_index=True)

    def __str__(self):
        return self.name


class GenreMovieMap(models.Model):
    id = models.AutoField(primary_key=True)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name='movies')
    movie_id = models.IntegerField(db_index=True)  

    class Meta:
        db_table = "genre_movie_map"
        unique_together = ('genre', 'movie_id')
        indexes = [
            models.Index(fields=['genre']),
            models.Index(fields=['movie_id']),
        ]




class GenreMovies(models.Model):
    genre = models.CharField(max_length=100, unique=True, db_index=True)
    movie_ids = models.JSONField() 
    top_movie_ids = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.genre
