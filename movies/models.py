# movies/models.py

from django.db import models
from django.conf import settings

class Genre(models.Model):
    tmdb_id = models.IntegerField(unique=True)
    name    = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Actor(models.Model):
    tmdb_id      = models.IntegerField(unique=True)
    name         = models.CharField(max_length=255)
    profile_path = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class Movie(models.Model):
    tmdb_id      = models.IntegerField(unique=True)
    title        = models.CharField(max_length=255)
    release_date = models.DateField()
    overview     = models.TextField()            # short description
    vote_average = models.FloatField()           # rating
    poster_path  = models.CharField(max_length=255)  # thumbnail path
    trailer_url  = models.URLField(blank=True)   # YouTube trailer link

    genres = models.ManyToManyField(Genre, related_name='movies')
    cast   = models.ManyToManyField(Actor, through='MovieCast')

    def __str__(self):
        return self.title


class MovieCast(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE)
    order = models.IntegerField()  # billing order in credits

    class Meta:
        unique_together = ('movie', 'actor')
        ordering = ['order']

    def __str__(self):
        return f"{self.actor.name} in {self.movie.title}"


class UserMovieEvent(models.Model):
    EVENT_CHOICES = [
        ('search', 'Search'),
        ('watch',  'Watch'),
        ('rate',   'Rate'),
    ]

    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    movie      = models.ForeignKey(Movie, on_delete=models.CASCADE, null=True, blank=True)
    event_type = models.CharField(max_length=10, choices=EVENT_CHOICES)
    timestamp  = models.DateTimeField(auto_now_add=True)
    metadata   = models.JSONField(blank=True, null=True)
    # metadata example: { "query": "Inception" } or { "rating": 4.5 }

    def __str__(self):
        return f"{self.user} {self.event_type} {self.movie or ''} at {self.timestamp}"




class RawMovie(models.Model):
    tmdb_id              = models.IntegerField(primary_key=True)
    title                = models.CharField(max_length=255)
    vote_average         = models.FloatField()
    vote_count           = models.IntegerField()
    status               = models.CharField(max_length=50)
    release_date         = models.DateField(null=True, blank=True)
    revenue              = models.BigIntegerField()
    runtime              = models.IntegerField(null=True, blank=True)
    adult                = models.BooleanField()
    backdrop_path        = models.CharField(max_length=255, blank=True)
    budget               = models.BigIntegerField()
    homepage             = models.URLField(blank=True)
    imdb_id              = models.CharField(max_length=20, blank=True)
    original_language    = models.CharField(max_length=10)
    original_title       = models.CharField(max_length=255)
    overview             = models.TextField(blank=True)
    popularity           = models.FloatField()
    poster_path          = models.CharField(max_length=255, blank=True)
    tagline              = models.CharField(max_length=255, blank=True)
    genres               = models.TextField(blank=True)  # pipe-delimited
    production_companies = models.TextField(blank=True)
    production_countries = models.TextField(blank=True)
    spoken_languages     = models.TextField(blank=True)
    keywords             = models.TextField(blank=True)

    index_score = models.FloatField(
        default=0.0,
        db_index=True,
        help_text="Precomputed vote_average * log(vote_count+1)"
    )

    # 1) Precomputed TF-IDF weights for overview+keywords+genres
    tfidf_vector = models.JSONField(
        default=dict, blank=True,
        help_text="Sparse TF-IDF weights"
    )
    # 2) L2 norm of that vector (for cosine)
    tfidf_norm = models.FloatField(
        default=0.0,
        help_text="L2 norm of tfidf_vector"
    )
    popularity_votes = models.FloatField(default=0.0, db_index=True, help_text="vote_average * log10(vote_count+1)")

    class Meta:
        indexes = [
            models.Index(fields=['index_score', '-release_date']),
            models.Index(fields=['-vote_average', '-vote_count']),
            models.Index(fields=['-release_date']),
            models.Index(fields=['genres']),
        ]

    def __str__(self):
        return f"{self.tmdb_id} – {self.title}"
