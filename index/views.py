import difflib, re
import random, json
from django.shortcuts   import render, get_object_or_404, redirect
from django.conf import settings
from django.core.cache  import cache
from django.db.models   import F, Func, ExpressionWrapper, FloatField, Q
from movies.models      import RawMovie
from django.core.paginator import Paginator

from django.http     import JsonResponse, HttpResponseRedirect
from django.urls     import reverse
from authentication.models import movie_user
from user_profile.models   import Watchlist
from django.db             import connection, models
from urllib.parse import quote
from django.views.decorators.http import require_POST
from index.models import GenreRecommendation, PrecomputedPool
import math
from math import log10
from elasticsearch import Elasticsearch


# Full set of search categories
SEARCH_CATEGORIES = [
    'Movies','TV Shows','Series','Short Films','Documentaries','Reality Shows',
    'Web Series','Animated Movies','Stand-up Comedy','Bollywood','Hollywood'
]

# Full set of search genres
SEARCH_GENRES = [
    'Action','Adventure','Comedy','Crime','Drama','Fantasy','Horror','Mystery',
    'Romance','Science Fiction','Thriller','War','Superhero','Family','Animation',
    'Western'
]



INDEX_SCORE_EXPR = ExpressionWrapper(
    F('vote_average') * Func(F('vote_count') + 1, function='LOG'),
    output_field=FloatField()
)

def get_top_random_by_genre(keywords,
                           sample_size=6,
                           pool_size=300,
                           pool_ttl=86400):
    
    cache_key = f"idx_pool_{keywords[0].lower().replace(' ', '_')}"
    pool = cache.get(cache_key)

    if pool is None:
        # 1) build OR‐filter
        q = Q()
        for kw in keywords:
            q |= Q(genres__icontains=kw)

        # 2+3) indexed ordering on `index_score` + release_date
        qs = (
            RawMovie.objects
                .filter(q)
                .order_by('-index_score', '-release_date')
                .values(
                    'tmdb_id','title','poster_path',
                    'release_date','runtime',
                    'vote_average','vote_count',
                    'genres'
                )[:pool_size]
        )

        pool = list(qs)
        cache.set(cache_key, pool, pool_ttl)

    # 5) every call gets a fresh random sample of size `sample_size`
    if len(pool) <= sample_size:
        selection = pool
    else:
        selection = random.sample(pool, sample_size)

    # 6) prepare genres_list
    for m in selection:
        m['genres_list'] = [g for g in m['genres'].split('|') if g]

    return selection

def index(request):
    genre_map = [
        ('Action', ['Action']),
        ('Drama',  ['Drama']),
        ('Comedy', ['Comedy']),
        ('Romance',['Romance']),
        ('Sci-Fi', ['Science Fiction','Sci-Fi','Sci Fi']),
    ]

    categories = [
        (name, get_top_random_by_genre(keywords))
        for name, keywords in genre_map
    ]
    try:
        user_id = request.session.get('user_id')
        if user_id:
            user = movie_user.objects.get(user_id=user_id)
            email = user.email
            username = email.split('@')[0]
        else:
            email = None
            username = None
    except movie_user.DoesNotExist:
        email = None  
        username = None


    return render(request, 'index/index.html', {
        'categories':     categories,
        'SEARCH_GENRES':  SEARCH_GENRES,
        'username':username,
    })





EXPLORE_SCORE_EXPR = ExpressionWrapper(
    F('vote_average') * Func(F('vote_count') + 1, function='LOG')
  + F('popularity') * 0.1
  + (F('revenue') / 1e8),
    output_field=FloatField()
)

PAGE_SIZE  = 48
MAX_PAGES  = 20
POOL_SIZE  = PAGE_SIZE * MAX_PAGES  # 960


ALL_GENRES = [
    'Action','Adventure','Comedy','Crime','Drama','Fantasy','Historical','Horror',
    'Mystery','Romance','Science Fiction','Thriller','War','Western','Animation',
    'Musical','Family','Biography','Political','Paranormal','Superhero'
]


ALL_CATEGORIES = [
    'Movies','TV Shows','Series','Short Films','Documentaries','Reality Shows',
    'Web Series','Biopics','Animated Movies','Children & Family',
    'Stand-up Comedy','Musical / Dance','Anthology','Sports & Competition',
    'Bollywood','Hollywood','Nepali Movies'
]





PAGE_SIZE  = 48    # 6 cols × 8 rows
MAX_PAGES  = 20    # cap at 20 pages → 960 IDs total

def explore(request):
    # 1) Read GET params
    category = request.GET.get('category', 'Movies')
    genre    = request.GET.get('genre')
    try:
        page_num = int(request.GET.get('page', '1'))
    except ValueError:
        page_num = 1

    # 2) Pick the correct precomputed key
    if genre:
        key = f"genre_{genre.replace(' ', '_')}"
    else:
        key = f"category_{category.replace(' ', '_')}"

    # 3) Load and shuffle the ID pool
    pool = []
    pool_obj = PrecomputedPool.objects.filter(key=key).first()
    if pool_obj:
        pool = list(pool_obj.movie_ids)
        random.shuffle(pool)

        # truncate so we never exceed MAX_PAGES
        max_items = MAX_PAGES * PAGE_SIZE
        if len(pool) > max_items:
            pool = pool[:max_items]

    # 4) Paginate
    paginator = Paginator(pool, PAGE_SIZE)
    page_obj  = paginator.get_page(page_num)

    # 5) Bulk-fetch and reorder movies for this page
    page_ids = page_obj.object_list
    movies_qs = RawMovie.objects.filter(tmdb_id__in=page_ids)
    movie_map = {m.tmdb_id: m for m in movies_qs}
    movies    = [movie_map[mid] for mid in page_ids if mid in movie_map]

    # 6) Prepare genres_list for template
    for m in movies:
        m.genres_list = [g.strip() for g in (m.genres or '').split('|') if g.strip()]

    # 7) Build the windowed pages_to_show
    total   = paginator.num_pages
    current = page_obj.number
    if total <= 7:
        pages_to_show = list(range(1, total+1))
    else:
        pages_to_show = [1]
        if current-2 > 2:
            pages_to_show.append(None)
        for p in range(max(2, current-2), min(total, current+2)+1):
            pages_to_show.append(p)
        if current+2 < total-1:
            pages_to_show.append(None)
        pages_to_show.append(total)

    # 8) (Optional) Get username
    username = None
    uid = request.session.get('user_id')
    if uid:
        try:
            u = movie_user.objects.get(user_id=uid, is_active=True)
            username = u.email.split('@',1)[0]
        except movie_user.DoesNotExist:
            pass

    # 9) Render exactly the context your template expects
    return render(request, 'index/explore.html', {
        'movies':           movies,
        'page_obj':         page_obj,
        'pages_to_show':    pages_to_show,
        'current_category': category,
        'current_genre':    genre,
        'username':         username,
    })











def toggle_watchlist(request):
  
    movie_id = request.POST.get('movie_id') if request.method == 'POST' else request.GET.get('movie_id')
    next_page = request.GET.get('next')  # only for GET


    user_id = request.session.get('user_id')
    if not user_id:

        toggle_url = reverse('index:toggle_watchlist')
        next_after = request.POST.get('next') or request.GET.get('next') or reverse('index:index')
        login_next = f"{toggle_url}?movie_id={movie_id}&next={next_after}"
        login_url = f"{reverse('login')}?next={quote(login_next, safe='')}"
        if request.method == 'POST':
            return JsonResponse({'redirect': login_url}, status=403)
        else:
            return HttpResponseRedirect(login_url)

    # Lookup user & movie
    try:
        user = movie_user.objects.get(pk=user_id)
        movie = RawMovie.objects.get(pk=movie_id)
    except (movie_user.DoesNotExist, RawMovie.DoesNotExist):
        if request.method == 'POST':
            return JsonResponse({'error': 'Not found'}, status=404)
        return HttpResponseRedirect(reverse('index:index'))

    # Perform toggle
    item, created = Watchlist.objects.get_or_create(user=user, movie=movie)
    if not created:
        item.delete()
        action = 'removed'
    else:
        action = 'added'

    # If AJAX POST, return JSON
    if request.method == 'POST':
        return JsonResponse({'status': 'ok', 'action': action})

    # Otherwise GET redirect mode
    # Redirect back to next_page if safe, else home
    return HttpResponseRedirect(next_page or reverse('index:index'))





FUZZY_POOL = 2000 

# Full dropdown lists
SEARCH_CATEGORIES = [
    'Movies','TV Shows','Series','Short Films','Documentaries','Reality Shows',
    'Web Series','Animated Movies','Stand-up Comedy','Bollywood','Hollywood'
]
SEARCH_GENRES = [
    'Action','Adventure','Comedy','Crime','Drama','Fantasy','Horror','Mystery',
    'Romance','Science Fiction','Thriller','War','Superhero','Family','Animation',
    'Western'
]

# index/views.py

QUERY_SYNONYMS = {
    'action':           ['action-adventure','action adventure'],
    'adventure':        ['action-adventure'],
    'comedy':           ['humor','funny','comedies'],
    'crime':            ['criminal','crime drama'],
    'drama':            ['dramatic'],
    'fantasy':          ['fantasy'],
    'horror':           ['scary','horror'],
    'mystery':          ['whodunit','mysteries'],
    'romance':          ['romantic'],
    'science fiction':  ['sci-fi','scifi','sci fi','sf'],
    'thriller':         ['suspense','thrillers'],
    'war':              ['war film','military'],
    'superhero':        ['comic book','super hero'],
    'family':           ['kids','children','family'],
    'animation':        ['anime','cartoon','animated'],
    'western':          ['westerns'],
}





from elasticsearch import Elasticsearch
from movies.models import RawMovie
from django.core.paginator import Paginator
from django.shortcuts import render
import re
from math import log10

def smart_normalize(s):
    s = s.lower()
    s = re.sub(r'[-_\'".:]', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

def search(request):
    es = Elasticsearch(
        "http://localhost:9200",
        basic_auth=("elastic", "hl_YsnaMxQ7Rp2IsWjMT")  # <-- Change this
    )
    user_query = request.GET.get('q', '').strip()
    smart_query = smart_normalize(user_query)
    page = int(request.GET.get('page', 1))
    per_page = 48

    # Elasticsearch query (returns all possibly matching movies)
    body = {
        "query": {
            "bool": {
                "should": [
                    {"match_phrase": {"smart_normalized_title": {"query": smart_query, "boost": 12}}},
                    {"match": {"title": {"query": user_query, "fuzziness": "AUTO", "boost": 6}}},
                    {"multi_match": {
                        "query": user_query,
                        "fields": ["keywords^3", "overview"],
                        "type": "best_fields"
                    }}
                ],
                "minimum_should_match": 1
            }
        },
        "size": 200
    }
    resp = es.search(index="movies", body=body)
    hits = resp["hits"]["hits"]
    # Maintain ES hit order for exact matches
    movie_ids = [hit["_source"]["movie_id"] for hit in hits if hit["_source"].get("movie_id")]

    # Fetch full movie info from DB for display fields
    movies_qs = RawMovie.objects.filter(tmdb_id__in=movie_ids)
    movie_map = {m.tmdb_id: m for m in movies_qs}
    all_movies = [movie_map[mid] for mid in movie_ids if mid in movie_map]

    def is_presentable(m):
        return (
            m.vote_count and m.vote_count > 0 and
            m.vote_average and m.vote_average > 0 and
            m.poster_path and m.title
        )

    exact_matches = []
    other_matches = []

    for m in all_movies:
        if smart_normalize(m.title) == smart_query:
            if is_presentable(m):
                exact_matches.append(m)
        else:
            if is_presentable(m):
                other_matches.append(m)


    # Sort "other" matches by popularity & quality
    def smart_score(m):
        return m.vote_average * log10(m.vote_count + 1)
    
    other_matches.sort(key=smart_score, reverse=True)
    exact_matches.sort(key=smart_score, reverse=True)
    # Combine: exact matches (keep ES order), then other matches (sorted)
    results = exact_matches + other_matches

    # Save search history if user is logged in
    user_id = request.session.get('user_id')
    if user_id:
        from user_profile.models import SearchHistory
        top10 = [m.tmdb_id for m in results[:10]]
        SearchHistory.objects.create(
            user_id=user_id,
            query=user_query,
            top_results=top10 or None
        )

    # Paginate combined list
    paginator = Paginator(results, per_page)
    page_obj = paginator.get_page(page)
    paginated_results = page_obj.object_list

    # Prepare genres_list for template
    for m in paginated_results:
        genres = m.genres or ""
        m.genres_list = [g.strip() for g in genres.split('|') if g.strip()]

    context = {
        "results": paginated_results,
        "q": user_query,
        "page_obj": page_obj,
        "current_category": "",
        "current_genre": "",
        "show_login_prompt": not bool(request.session.get('user_id')),
    }
    return render(request, 'index/search_results.html', context)




import difflib
from math import log10
from itertools import combinations

def cosine_sim(vec1, norm1, vec2, norm2):
    if not vec1 or not vec2 or not norm1 or not norm2:
        return 0.0
    dot = 0.0
    for k, v in vec1.items():
        dot += v * vec2.get(k, 0.0)
    return dot / (norm1 * norm2)

def is_series_match(title1, title2, keywords1=None, keywords2=None):
    import re
    t1 = re.sub(r'[^a-z0-9]+', '', title1.lower())
    t2 = re.sub(r'[^a-z0-9]+', '', title2.lower())
    # Title direct fuzzy match
    if t1 in t2 or t2 in t1 or difflib.SequenceMatcher(None, t1, t2).ratio() > 0.80:
        return True
    # Keyword overlap (if you have keywords)
    if keywords1 and keywords2:
        set1 = set([k.strip().lower() for k in keywords1.split(',') if k.strip()])
        set2 = set([k.strip().lower() for k in keywords2.split(',') if k.strip()])
        if set1 and set2 and len(set1 & set2) > 2:
            return True
    return False

def recommend_bucketed_series_hybrid(movie, num=24):
    from index.models import GenreMovies
    from movies.models import RawMovie

    import time
    t_total = time.time()

    genres = set([g.strip() for g in (movie.genres or '').replace('|', ',').split(',') if g.strip()])
    genre_count = len(genres)
    if not genres or genre_count == 0:
        return []

    orig_vec = movie.tfidf_vector or {}
    orig_norm = movie.tfidf_norm or 1.0
    current_id = movie.tmdb_id

    genre_rows = {}
    for genre in genres:
        try:
            genre_rows[genre] = GenreMovies.objects.get(genre=genre)
        except GenreMovies.DoesNotExist:
            continue

    t_genre_rows = time.time()
    print("Genre row fetching took:", round(t_genre_rows - t_total, 3), "seconds")

    used_ids = set()
    final_results = []

    movie_title = movie.title or ""
    movie_keywords = getattr(movie, "keywords", "")

    t_buckets = time.time()
    print("Preparation before buckets took:", round(t_buckets - t_genre_rows, 3), "seconds")

    for overlap in range(genre_count, 0, -1):
        t_fetch = time.time()
        bucket_ids = set()
        if overlap == 1:
            for genre, row in genre_rows.items():
                bucket_ids.update(row.top_movie_ids[:400])
        else:
            for genre_subset in combinations(genres, overlap):
                id_sets = []
                for g in genre_subset:
                    if g in genre_rows:
                        id_sets.append(set(genre_rows[g].movie_ids))
                if len(id_sets) == overlap:
                    bucket_ids.update(set.intersection(*id_sets))

        bucket_ids.difference_update(used_ids)
        bucket_ids.discard(current_id)
        if not bucket_ids:
            continue
        
        if len(bucket_ids) > 2000:
            bucket_ids = set(list(bucket_ids)[:2000])
    
        def batched_ids(ids, batch_size=500):
            ids = list(ids)
            for i in range(0, len(ids), batch_size):
                yield ids[i:i+batch_size]

        movies = []
        print(f"Bucket with overlap={overlap} has {len(bucket_ids)} IDs")

        for id_batch in batched_ids(bucket_ids, batch_size=500):
            movies.extend(RawMovie.objects.only(
                'tmdb_id', 'title', 'genres', 'poster_path', 'vote_average', 'vote_count',
                'popularity_votes', 'tfidf_vector', 'tfidf_norm', 'keywords'
            ).filter(tmdb_id__in=id_batch))

        
        print(f"Bucket with overlap={overlap} ORM fetch took:", round(time.time() - t_fetch, 3), "seconds")

        strong_matches = []
        normal_matches = []
        for m in movies:
            if not (m.poster_path and m.vote_average and m.vote_count and m.vote_average >= 5 and m.vote_count >= 100):
                continue
            cos = cosine_sim(orig_vec, orig_norm, m.tfidf_vector or {}, m.tfidf_norm or 1.0)
            pop = m.popularity_votes or 0

            # --- Franchise/part detection (title and keywords) ---
            if is_series_match(movie_title, m.title or "", movie_keywords, getattr(m, "keywords", "")):
                strong_matches.append((cos, pop, m))
            else:
                normal_matches.append((cos, pop, m))

        # Normalize popularity for each group
        for group in [strong_matches, normal_matches]:
            if group:
                max_pop_score = max((pop for _, pop, _ in group), default=1)
                def composite_score(cos, pop):
                    norm_pop = pop / max_pop_score if max_pop_score else 0
                    return 0.8 * cos + 0.2 * norm_pop
                group.sort(key=lambda x: composite_score(x[0], x[1]), reverse=True)

        t_scoring = time.time()
        print(f"Scoring and sorting for overlap={overlap} took:", round(t_scoring - t_fetch, 3), "seconds")
        # Add franchise/strong matches first, then normal, until 24
        for _, _, m in strong_matches:
            if len(final_results) < num:
                final_results.append(m)
                used_ids.add(m.tmdb_id)
        for _, _, m in normal_matches:
            if len(final_results) < num:
                final_results.append(m)
                used_ids.add(m.tmdb_id)
        if len(final_results) >= num:
            break

    return final_results






def movie_detail(request, tmdb_id):
    # --- 1) Session guard ---
    user_id = request.session.get('user_id')
    if not user_id:
        next_url = reverse('index:movie_detail', args=[tmdb_id])
        return redirect(f"{reverse('login')}?next={next_url}")

    # --- 2) Load movie & watchlist flag ---
    movie = get_object_or_404(RawMovie, tmdb_id=tmdb_id)
    in_watchlist = Watchlist.objects.filter(
        user_id=user_id, movie=movie
    ).exists()

    # --- 3) Split genres ---
    raw = movie.genres or ''
    parts = [g.strip() for g in __import__('re').split(r'[\|,]+', raw) if g.strip()]
    genres = parts

    rec_movies = recommend_bucketed_series_hybrid(movie, num=24)
    recommendation_rows = [
        rec_movies[i: i+6] for i in range(0, len(rec_movies), 6)
    ]

    # After fetching and before sending to template:
    for row in recommendation_rows:
        for rec in row:
            genres = rec.genres or ""
            rec.genres_list = [g.strip() for g in genres.replace('|', ',').split(',') if g.strip()]



    # --- Render as before ---
    return render(request, 'index/movie_details.html', {
        'm': movie,
        'in_watchlist': in_watchlist,
        'genres_list': [g.strip() for g in (movie.genres or '').replace('|', ',').split(',') if g.strip()],
        'TMDB_API_KEY': settings.TMDB_API_KEY,
        'recommendation_rows': recommendation_rows,
    })






@require_POST
def toggle_watchlist_ajax(request):
    # 1) Parse JSON body
    try:
        payload = json.loads(request.body)
        movie_id = payload.get('movie_id')
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    # 2) Require login
    user_id = request.session.get('user_id')
    if not user_id:
        # tell the frontend to redirect to login
        login_next = request.META.get('HTTP_REFERER', reverse('index:index'))
        login_url  = f"{reverse('login')}?next={login_next}"
        return JsonResponse({'redirect': login_url}, status=403)

    # 3) Lookup user & movie
    user  = get_object_or_404(movie_user, pk=user_id)
    movie = get_object_or_404(RawMovie,   pk=movie_id)

    # 4) Toggle
    item, created = Watchlist.objects.get_or_create(user=user, movie=movie)
    if not created:
        item.delete()
        action = 'removed'
    else:
        action = 'added'

    return JsonResponse({'status': 'ok', 'action': action})
