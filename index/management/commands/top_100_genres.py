from django.core.management.base import BaseCommand
from movies.models import RawMovie
from index.models import GenreMovies
from math import log10
from django.db import models

class Command(BaseCommand):
    help = "Precompute top 100 movies per genre for fast recommendations"

    def handle(self, *args, **kwargs):
        for row in GenreMovies.objects.all():
            # Only fetch high-quality candidates
            ids = (
                RawMovie.objects
                .filter(
                    genres__icontains=row.genre,
                    vote_count__gt=0,
                    vote_average__gt=0,
                    poster_path__isnull=False
                )
                .annotate(
                    popularity_score=models.ExpressionWrapper(
                        models.F('vote_average') * models.Func(models.F('vote_count') + 1, function='LOG') +
                        models.F('popularity') / 10 +
                        models.F('revenue') / 1e8,
                        output_field=models.FloatField()
                    )
                )
                .order_by('-popularity_score')
                .values_list('tmdb_id', flat=True)[:100]
            )
            row.top_movie_ids = list(ids)
            row.save(update_fields=['top_movie_ids'])
        self.stdout.write(self.style.SUCCESS("Top 100 movies per genre updated!"))
