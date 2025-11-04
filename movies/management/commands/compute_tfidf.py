# movies/management/commands/compute_tfidf.py

from django.core.management.base import BaseCommand
from sklearn.feature_extraction.text import TfidfVectorizer
from movies.models import RawMovie
import numpy as np
import math

class Command(BaseCommand):
    help = "Compute TF-IDF vectors for all movies (chunked + bulk updates)"

    def handle(self, *args, **opts):
        qs = RawMovie.objects.all()
        total = qs.count()
        self.stdout.write(f"Total movies: {total}")

        # 1) Gather all texts & IDs (in memory)
        texts = []
        ids   = []
        for m in qs:
            txt = " ".join(filter(None, [m.overview, m.keywords, m.genres]))
            texts.append(txt.lower())
            ids.append(m.tmdb_id)

        # 2) Fit on full corpus (slow!)
        vec   = TfidfVectorizer(max_features=5000, stop_words='english')
        vec.fit(texts)
        vocab = vec.get_feature_names_out()
        self.stdout.write("✔ TF-IDF vocabulary built")

        # 3) Process in chunks to show progress & do bulk_update
        chunk_size = 10_000
        for start in range(0, total, chunk_size):
            end = min(start + chunk_size, total)
            sub_texts = texts[start:end]
            sub_ids   = ids[start:end]

            # 3a) Transform only this chunk
            X_chunk = vec.transform(sub_texts)

            # 3b) Build instances in memory
            movies = list(RawMovie.objects.filter(tmdb_id__in=sub_ids))
            id_map = {m.tmdb_id: m for m in movies}

            # 3c) Fill in tfidf_vector & tfidf_norm
            for idx, tmdb_id in enumerate(sub_ids):
                row = X_chunk[idx].tocoo()
                data = row.data
                cols = row.col
                vect = {vocab[c]: float(data[i]) for i,c in enumerate(cols)}
                norm = float(math.sqrt((data**2).sum()))

                inst = id_map.get(tmdb_id)
                if inst:
                    inst.tfidf_vector = vect
                    inst.tfidf_norm   = norm

            # 3d) Bulk‐update this chunk
            RawMovie.objects.bulk_update(
                movies,
                ['tfidf_vector','tfidf_norm'],
                batch_size=1000
            )

            self.stdout.write(f"Processed {end}/{total}")

        self.stdout.write(self.style.SUCCESS("✔ All TF-IDF vectors computed."))
