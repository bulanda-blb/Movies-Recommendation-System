from django.db import models
from authentication.models import movie_user
from movies.models         import RawMovie

class Watchlist(models.Model):
    user  = models.ForeignKey(movie_user, on_delete=models.CASCADE)
    movie = models.ForeignKey(RawMovie, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user','movie')
        verbose_name_plural = 'Watchlist Items'

    def __str__(self):
        return f"{self.user.email} → {self.movie.title}"



class SearchHistory(models.Model):
    user = models.ForeignKey(
        movie_user,
        on_delete=models.CASCADE,
        related_name='search_histories'
    )
    
    query = models.CharField(
        max_length=255,
        help_text="The raw search text the user entered."
    )
    top_results = models.JSONField(
        null=True,
        blank=True,
        help_text="List of up to 10 TMDb IDs that were shown as top results."
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When the search was performed."
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = "Search Histories"

    def __str__(self):
        return f"{self.user.email} @ {self.timestamp:%Y-%m-%d %H:%M} → {self.query}"
