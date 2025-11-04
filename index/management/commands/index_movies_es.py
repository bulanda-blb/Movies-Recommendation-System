from django.core.management.base import BaseCommand
from index.models import GenreMovieSearch  # Use your search model here
from elasticsearch import Elasticsearch, helpers
import re

def smart_normalize(s):
    s = s.lower()
    s = re.sub(r'[-_\'".:]', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

class Command(BaseCommand):
    help = "Index movies with smart normalization into Elasticsearch"

    def handle(self, *args, **kwargs):
        es = Elasticsearch(
            "http://localhost:9200",
            basic_auth=("elastic", "hl_YsnaMxQ7Rp2IsWjMT")
        )

        # 1. Delete old index (for dev, safe to do)
        if es.indices.exists(index="movies"):
            es.indices.delete(index="movies")

        # 2. Create new index (standard analyzer is fine here, no ngram needed with smart_normalize)
        es.indices.create(
            index="movies",
            body={
                "mappings": {
                    "properties": {
                        "movie_id": {"type": "integer"},
                        "title": {"type": "text"},
                        "smart_normalized_title": {"type": "text"},
                        "keywords": {"type": "text"},
                        "overview": {"type": "text"}
                    }
                }
            }
        )

        # 3. Bulk index movie data
        actions = []
        for m in GenreMovieSearch.objects.all().iterator():
            actions.append({
                "_index": "movies",
                "_id": m.movie_id,
                "_source": {
                    "movie_id": m.movie_id,
                    "title": m.title,
                    "smart_normalized_title": smart_normalize(m.title),
                    "keywords": m.keywords,
                    "overview": m.overview,
                }
            })
            if len(actions) >= 5000:
                helpers.bulk(es, actions)
                actions = []
        if actions:
            helpers.bulk(es, actions)
        print("Done indexing with smart normalization!")
