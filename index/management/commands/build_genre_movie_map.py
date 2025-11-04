from django.core.management.base import BaseCommand
from movies.models import RawMovie
from index.models import GenreMovies

class Command(BaseCommand):
    help = "One row per unique single genre (comma separated). Each row has JSON list of all movie IDs with that genre."

    def handle(self, *args, **kwargs):
        import time
        from collections import defaultdict

        start = time.time()
        GenreMovies.objects.all().delete()
        self.stdout.write("Cleared old GenreMovies.")

        genre_to_movies = defaultdict(set)

        # Only process each movie's genres as comma-separated tags!
        for m in RawMovie.objects.only('tmdb_id', 'genres').iterator():
            if not m.genres:
                continue
            # Split on comma and strip whitespace, lower if needed for true uniqueness
            tags = [g.strip() for g in m.genres.split(',') if g.strip()]
            for tag in tags:
                genre_to_movies[tag].add(m.tmdb_id)

        # Create one row per unique genre
        objs = [GenreMovies(genre=genre, movie_ids=list(ids)) for genre, ids in genre_to_movies.items()]
        GenreMovies.objects.bulk_create(objs)
        self.stdout.write(self.style.SUCCESS(
            f"Done! {len(objs)} unique genres (should be ~25) in {time.time() - start:.2f} seconds."
        ))
