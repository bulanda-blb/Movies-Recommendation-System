

import csv
from django.core.management.base import BaseCommand
from movies.models import RawMovie

BATCH_SIZE = 1000

class Command(BaseCommand):
    help = 'Bulk-load the TMDb movies_metadata CSV into RawMovie'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_path',
            type=str,
            help='Path to the movies_metadata.csv file'
        )

    def handle(self, *args, **options):
        path = options['csv_path']
        batch = []
        total = 0

        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # build RawMovie instance
                batch.append(RawMovie(
                    tmdb_id=int(row['id']),
                    title=row['title'][:255],
                    vote_average=float(row['vote_average'] or 0),
                    vote_count=int(row['vote_count'] or 0),
                    status=row['status'],
                    release_date=row['release_date'] or None,
                    revenue=int(row['revenue'] or 0),
                    runtime=int(row['runtime'] or 0),
                    adult=(row['adult'].lower() == 'true'),
                    backdrop_path=row['backdrop_path'] or '',
                    budget=int(row['budget'] or 0),
                    homepage=row['homepage'] or '',
                    imdb_id=row['imdb_id'] or '',
                    original_language=row['original_language'] or '',
                    original_title=row['original_title'][:255],
                    overview=row['overview'] or '',
                    popularity=float(row['popularity'] or 0),
                    poster_path=row['poster_path'] or '',
                    tagline=row['tagline'] or '',
                    genres=row['genres'] or '',
                    production_companies=row['production_companies'] or '',
                    production_countries=row['production_countries'] or '',
                    spoken_languages=row['spoken_languages'] or '',
                    keywords=row['keywords'] or '',
                ))
                # When batch is full, bulk create
                if len(batch) >= BATCH_SIZE:
                    RawMovie.objects.bulk_create(batch, ignore_conflicts=True)
                    total += len(batch)
                    self.stdout.write(f"Inserted {total} rows...")
                    batch.clear()

            # Insert any remaining
            if batch:
                RawMovie.objects.bulk_create(batch, ignore_conflicts=True)
                total += len(batch)
                self.stdout.write(f"Inserted {total} rows.")

        self.stdout.write(self.style.SUCCESS(f"Finished loading {total} movies."))
