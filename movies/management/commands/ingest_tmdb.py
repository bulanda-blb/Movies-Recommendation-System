# movies/management/commands/ingest_tmdb.py

import os
import requests
from django.core.management.base import BaseCommand
from django.utils import timezone
from movies.models import Movie, Genre, Actor, MovieCast

API_KEY = os.getenv('TMDB_API_KEY')
BASE    = 'https://api.themoviedb.org/3'

class Command(BaseCommand):
    help = 'Ingest TMDb metadata into the local database'

    def handle(self, *args, **options):
        page = 1
        while True:
            resp = requests.get(
                f"{BASE}/discover/movie",
                params={'api_key': API_KEY, 'page': page}
            ).json()

            for item in resp.get('results', []):
                self.ingest_movie(item['id'])

            if page >= resp.get('total_pages', 0):
                break
            page += 1

        self.stdout.write(self.style.SUCCESS("Ingestion complete."))

    def ingest_movie(self, tmdb_id):
        # 1) Fetch full details + credits + videos
        params = {
            'api_key': API_KEY,
            'append_to_response': 'credits,videos'
        }
        data = requests.get(f"{BASE}/movie/{tmdb_id}", params=params).json()

        # 2) Upsert Movie core fields
        movie, _ = Movie.objects.update_or_create(
            tmdb_id=tmdb_id,
            defaults={
                'title':        data.get('title', ''),
                'release_date': data.get('release_date') or timezone.now().date(),
                'overview':     data.get('overview', ''),
                'vote_average': data.get('vote_average', 0.0),
                'poster_path':  data.get('poster_path', '') or '',
                'trailer_url':  self._extract_trailer(data.get('videos', {})),
            }
        )

        # 3) Sync genres
        genre_objs = []
        for g in data.get('genres', []):
            obj, _ = Genre.objects.get_or_create(
                tmdb_id=g['id'],
                defaults={'name': g['name']}
            )
            genre_objs.append(obj)
        movie.genres.set(genre_objs)

        # 4) Sync top-10 cast with update_or_create
        for c in data.get('credits', {}).get('cast', [])[:10]:
            actor, _ = Actor.objects.get_or_create(
                tmdb_id=c['id'],
                defaults={
                    'name':         c.get('name', ''),
                    'profile_path': c.get('profile_path') or ''
                }
            )
            MovieCast.objects.update_or_create(
                movie=movie,
                actor=actor,
                defaults={'order': c.get('order', 0)}
            )

    def _extract_trailer(self, videos):
        for v in videos.get('results', []):
            if v.get('site') == 'YouTube' and v.get('type') == 'Trailer':
                return f"https://www.youtube.com/watch?v={v.get('key')}"
        return ''
