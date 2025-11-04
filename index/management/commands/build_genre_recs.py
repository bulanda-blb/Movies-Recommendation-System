# index/management/commands/build_genre_recs.py

import re
from django.core.management.base import BaseCommand
from index.models import GenreRecommendation
from movies.models import RawMovie

# Number of top movies to keep per genre
TOP_PER_GENRE = 100

class Command(BaseCommand):
    help = "Build and store top-N tmdb_id lists per distinct genre"

    def handle(self, *args, **options):
        # 1) Gather all raw genre strings
        all_values = RawMovie.objects.values_list('genres', flat=True)

        # 2) Split into individual genre names on '|' or ',' and strip whitespace
        genre_set = set()
        splitter = re.compile(r'[\|,]+')
        for raw in all_values:
            if not raw:
                continue
            parts = splitter.split(raw)
            for p in parts:
                name = p.strip()
                if name:
                    genre_set.add(name)

        self.stdout.write(self.style.SUCCESS(f"Found {len(genre_set)} distinct genres."))

        # 3) For each genre, grab the top TOP_PER_GENRE movies by index_score + release_date
        for genre in sorted(genre_set):
            qs = RawMovie.objects.filter(genres__icontains=genre)
            top_ids = list(
                qs
                .order_by('-index_score', '-release_date')
                .values_list('tmdb_id', flat=True)[:TOP_PER_GENRE]
            )

            obj, created = GenreRecommendation.objects.update_or_create(
                genre=genre,
                defaults={'movie_ids': top_ids}
            )
            verb = "Created" if created else "Updated"
            self.stdout.write(
                self.style.SUCCESS(f"{verb} recs for genre {genre!r}: {len(top_ids)} movies")
            )
