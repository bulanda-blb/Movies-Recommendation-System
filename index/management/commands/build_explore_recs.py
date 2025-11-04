import re
from django.core.management.base import BaseCommand
from django.db.models import Q, F
from index.models import GenreRecommendation, PrecomputedPool
from movies.models import RawMovie

# how many to precompute for each key
TOP_PER_KEY = 1000  

# categories & their queryset filters
CATEGORY_FILTERS = {
    'Movies':          Q(),  # no filter = all movies
    'Documentaries':  Q(genres__icontains='Documentary'),
    'Animated Movies':(
        Q(genres__icontains='Animation') |
        Q(keywords__icontains='anime') |
        Q(keywords__icontains='cartoon')
    ),
    'Stand-up Comedy':(
        Q(genres__icontains='Comedy') &
        Q(keywords__icontains='stand-up')
    ),
    'Bollywood':      Q(original_language='hi') | Q(keywords__icontains='bollywood'),
    'Hollywood':      Q(original_language='en') & ~Q(keywords__icontains='bollywood'),
}

GENRE_SPLIT_RE = re.compile(r'[\|,]+')

class Command(BaseCommand):
    help = "Build precomputed pools for explore: categories and genres"

    def handle(self, *args, **options):
        # 1) Build for categories
        for cat_name, filt in CATEGORY_FILTERS.items():
            qs = RawMovie.objects.filter(filt)
            top_ids = list(
                qs.order_by('-index_score', '-release_date')
                  .values_list('tmdb_id', flat=True)[:TOP_PER_KEY]
            )
            key = f"category_{cat_name.replace(' ', '_')}"
            PrecomputedPool.objects.update_or_create(
                key=key, defaults={'movie_ids': top_ids}
            )
            self.stdout.write(
                self.style.SUCCESS(f"Built pool for {key}: {len(top_ids)}")
            )

        # 2) Gather all distinct genres
        raw_list = RawMovie.objects.values_list('genres', flat=True).distinct()
        genres = set()
        for raw in raw_list:
            if not raw: continue
            for g in GENRE_SPLIT_RE.split(raw):
                name = g.strip()
                if name:
                    genres.add(name)

        # 3) Build for each genre
        for genre in sorted(genres):
            qs = RawMovie.objects.filter(genres__icontains=genre)
            top_ids = list(
                qs.order_by('-index_score', '-release_date')
                  .values_list('tmdb_id', flat=True)[:TOP_PER_KEY]
            )
            key = f"genre_{genre.replace(' ', '_')}"
            PrecomputedPool.objects.update_or_create(
                key=key, defaults={'movie_ids': top_ids}
            )
            self.stdout.write(
                self.style.SUCCESS(f"Built pool for {key}: {len(top_ids)}")
            )
