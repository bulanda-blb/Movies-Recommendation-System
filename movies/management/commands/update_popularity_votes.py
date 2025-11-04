from django.core.management.base import BaseCommand
from movies.models import RawMovie
from math import log10

class Command(BaseCommand):
    help = "Update all RawMovies with precomputed popularity_votes score"

    def handle(self, *args, **kwargs):
        BATCH_SIZE = 10000
        total = RawMovie.objects.count()
        updated = 0

        # Use .only to reduce memory, and update in batches for speed
        qs = RawMovie.objects.only('pk', 'vote_average', 'vote_count')

        batch = []
        for m in qs.iterator(chunk_size=BATCH_SIZE):
            va = m.vote_average or 0.0
            vc = m.vote_count or 0
            m.popularity_votes = va * log10(vc + 1)
            batch.append(m)
            if len(batch) >= BATCH_SIZE:
                RawMovie.objects.bulk_update(batch, ['popularity_votes'])
                updated += len(batch)
                self.stdout.write(f"Updated {updated}/{total}")
                batch = []
        # Final batch
        if batch:
            RawMovie.objects.bulk_update(batch, ['popularity_votes'])
            updated += len(batch)
            self.stdout.write(f"Updated {updated}/{total}")

        self.stdout.write(self.style.SUCCESS("Done updating popularity_votes for all movies!"))
