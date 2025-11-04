from django.core.management.base import BaseCommand
from movies.models import RawMovie
from index.models import GenreMovieSearch
import re

def normalize(s):
    return re.sub(r'[^a-z0-9]+', ' ', s.lower()).strip()

class Command(BaseCommand):
    help = "Populate GenreMovieSearch (movie_search) from RawMovie"

    def handle(self, *args, **kwargs):
        print("Deleting old entries...")
        GenreMovieSearch.objects.all().delete()
        print("Populating new table (bulk)...")

        objs = []
        BATCH_SIZE = 10000
        count = 0

        movies = RawMovie.objects.all().iterator()
        for movie in movies:
            objs.append(GenreMovieSearch(
                movie_id=movie.tmdb_id,
                title=movie.title,
                normalized_title=normalize(movie.title),
                keywords=movie.keywords or '',
                overview=movie.overview or '',
            ))
            count += 1
            if len(objs) >= BATCH_SIZE:
                GenreMovieSearch.objects.bulk_create(objs, batch_size=BATCH_SIZE)
                print(f"Inserted {count} rows...")
                objs = []
        if objs:
            GenreMovieSearch.objects.bulk_create(objs, batch_size=BATCH_SIZE)
            print(f"Inserted final {len(objs)} rows. Total: {count}")
        print("Done.")
