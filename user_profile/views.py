
from django.shortcuts import render, redirect
from django.contrib import messages
from authentication.models import movie_user, Preference

import re, random
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.urls import reverse
from .models import Watchlist

from django.core.paginator import Paginator
from django.db.models      import Q
from authentication.models import movie_user, Preference
from movies.models         import RawMovie

import json
from django.http      import HttpResponseForbidden
from .models import SearchHistory

from django.core.cache import cache
import math
from django.db.models      import F, Func, ExpressionWrapper, FloatField

EMAIL_RE = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
PWD_RE   = re.compile(r'^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,16}$')

def preferences(request):
    # 1) Grab user_id from session and load the user object
    user_id = request.session.get('user_id')
    print(user_id)
    if not user_id:
        messages.error(request, "Please log in first.")
        return redirect('login')

    try:
        user = movie_user.objects.get(user_id=user_id, is_active=True)
    except movie_user.DoesNotExist:
        messages.error(request, "Invalid user.")
        return redirect('login')

    # 2) Ensure a Preference record exists
    prefs, created = Preference.objects.get_or_create(user=user)

    if request.method == 'POST':

        # now proceed to overwrite and save
        prefs.genres           = request.POST.getlist('genre')
        prefs.moods            = request.POST.getlist('mood')
        prefs.preferred_length = request.POST.get('length', '')
        prefs.context          = request.POST.get('context', '')
        prefs.frequency        = request.POST.get('frequency', '')
        prefs.subtitles        = (request.POST.get('subtitles') == 'Yes')
        prefs.era              = request.POST.getlist('era')
        prefs.content_type     = request.POST.getlist('type')
        prefs.save()
        
        return redirect('user_profile:preferences')

    # 3) On GET, just render with whatever prefs already are
    return render(request, 'user_profile/preferences.html', {
        'prefs': prefs
    })







ALL_GENRES = [
    'Action','Adventure','Comedy','Crime','Drama','Fantasy','Historical','Horror',
    'Mystery','Romance','Science Fiction','Thriller','War','Western','Animation',
    'Musical','Family','Biography','Political','Paranormal','Superhero'
]

def watchlist(request):
    # — 1) Ensure logged in —
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')  # or preferences with next, as desired

    # — 2) Read sorting & filtering params —
    sort_key   = request.GET.get('sort', 'date')   # date, rating, alpha
    genre_key  = request.GET.get('genre', 'all')   # lowercase e.g. "action"

    # — 3) Base QS: Watchlist items for this user —
    try:
        user = movie_user.objects.get(pk=user_id)
    except movie_user.DoesNotExist:
        return redirect('login')

    qs = Watchlist.objects.filter(user=user).select_related('movie')

    # — 4) Genre filter (if not "all") —
    if genre_key != 'all':
        # match across genres, keywords, overview
        title = genre_key.replace('-', ' ').title()
        qs = qs.filter(
            Q(movie__genres__icontains=title) |
            Q(movie__keywords__icontains=genre_key) |
            Q(movie__overview__icontains=title)
        )

    # — 5) Convert to list of dicts for easy template use —
    items = []
    for w in qs:
        m = w.movie
        items.append({
            'tmdb_id':       m.tmdb_id,
            'title':         m.title,
            'poster_path':   m.poster_path,
            'release_date':  m.release_date,
            'runtime':       m.runtime,
            'vote_average':  m.vote_average,
            'vote_count':    m.vote_count,
            'genres':        m.genres,
            'genres_list':   [g for g in m.genres.split('|') if g],
            'added_at':      w.added_at,
        })

    # — 6) Sort in Python (small N) or DB if large —
    if sort_key == 'rating':
        items.sort(key=lambda x: x['vote_average'], reverse=True)
    elif sort_key == 'alpha':
        items.sort(key=lambda x: x['title'])
    else:  # date
        items.sort(key=lambda x: x['added_at'], reverse=True)

    # — 7) Paginate (optional — you can remove if you want all) —
    paginator = Paginator(items, 48)
    page_obj  = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'user_profile/watchlist.html', {
        'items':       page_obj.object_list,
        'page_obj':    page_obj,
        'all_genres':  ['all'] + [g.lower().replace(' ', '-') for g in ALL_GENRES],
        'current_sort':  sort_key,
        'current_genre': genre_key,
    })



def edit_profile(request):
    # Helper to detect AJAX
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    # 1) Session check
    uid = request.session.get('user_id')
    if not uid:
        return redirect(f"{reverse('login')}?next={reverse('user_profile:edit')}")

    try:
        user = movie_user.objects.get(user_id=uid, is_active=True)
    except movie_user.DoesNotExist:
        return redirect('login')

    # 2) AJAX-only for notification toggle
    if request.method == 'POST' and is_ajax:
        action = request.POST.get('action')
        if action == 'notify':
            notify = request.POST.get('notify') == 'true'
            user.notification_on = notify
            user.save(update_fields=['notification_on'])
            return JsonResponse({'status':'ok','notify': notify})
        return JsonResponse({'status':'error','error':'Unknown AJAX action'}, status=400)

    # 3) Normal POST for email, password, deactivate
    if request.method == 'POST' and not is_ajax:
        action = request.POST.get('action')

        if action == 'email':
            new_email = request.POST.get('new_email','').strip()
            if not EMAIL_RE.match(new_email):
                messages.error(request, "Invalid email format.")
            else:
                user.email = new_email
                user.save(update_fields=['email'])
                messages.success(request, "Email updated successfully.")
            return redirect('user_profile:edit_profile')

        if action == 'password':
            pw  = request.POST.get('new_password','')
            cpw = request.POST.get('confirm_password','')
            if pw != cpw:
                messages.error(request, "Passwords do not match.")
            elif not PWD_RE.match(pw):
                messages.error(request, "Password must be 8–16 chars, include uppercase, digit & special.")
            else:
                user.password = make_password(pw)
                user.save(update_fields=['password'])
                messages.success(request, "Password changed successfully.")
            return redirect('user_profile:edit_profile')

        if action == 'deactivate':
            user.is_active = False
            user.save(update_fields=['is_active'])
            del request.session['user_id']
            return redirect('login')

    # 4) GET → render
    watchlist_count = Watchlist.objects.filter(user_id=uid).count()  
    history_count   = SearchHistory.objects.filter(user_id=uid).count()  

    return render(request, 'user_profile/edit_profile.html', {
        'email': user.email,
        'notify': user.notification_on,
        'watchlist_count': watchlist_count,
        'history_count': history_count,
    })





def history(request):
    # require login
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    # fetch all searches for this user
    histories = SearchHistory.objects.filter(
        user_id=user_id
    ).order_by('-timestamp')
    return render(request, 'user_profile/history.html', {
        'histories': histories
    })

def delete_history(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
            hid = payload.get('id')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Bad request'}, status=400)

        
        try:
            entry = SearchHistory.objects.get(pk=hid, user_id=user_id)
            entry.delete()
            return JsonResponse({'status': 'ok'})
        except SearchHistory.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)

    return HttpResponseForbidden()






from .utils                import build_preference_set
from user_profile.models   import SearchHistory


POP_SCORE = ExpressionWrapper(
      F('vote_average') * Func(F('vote_count')+1, function='LOG')
    + F('popularity') * 0.1
    + (F('revenue') / 1e8),
    output_field=F('vote_average').field if False else None  # we'll ignore this hack and treat pop_score as float below
)

# weights
W_WATCH   = 0.50
W_SEARCH  = 0.20
W_PREF    = 0.20
W_POP     = 0.10

PAGE_SIZE = 45
POOL_SIZE = 1000
CACHE_TTL = 86400
def recommendations(request):
    uid = request.session.get('user_id')
    if not uid:
        return redirect('user_profile:preferences')

    
    cache_key = f"user_recs_{uid}"
    scored = cache.get(cache_key)
    if scored is None:
        # --- 1) Gather seed vectors ---
        # a) watchlist seeds
        watch_ids = list(
        movie_user.objects.get(pk=uid)
            .watchlist_set.values_list('movie__tmdb_id', flat=True)
        )
        watch_seeds = list(
        RawMovie.objects.filter(tmdb_id__in=watch_ids)
                .values('tmdb_id','tfidf_vector','tfidf_norm')
        )

        # b) search history seeds (top 5 results per recent 5 searches)
        hist = SearchHistory.objects.filter(user_id=uid).order_by('-timestamp')[:5]
        search_ids = []
        for h in hist:
            if h.top_results:
                search_ids += h.top_results[:5]
        search_seeds = list(
        RawMovie.objects.filter(tmdb_id__in=search_ids)
                .values('tmdb_id','tfidf_vector','tfidf_norm')
        )

        # c) preference set (just a python set for quick membership)
        pref_set = build_preference_set(uid)  
        # e.g. {"Romance","Drama","Family"} 

        # --- 2) Candidate pool by popularity ---
        raw_candidates = list(
        RawMovie.objects
            .annotate(pop_score=POP_SCORE)
            .order_by('-pop_score')[:POOL_SIZE]
            .values(
            'tmdb_id','title','poster_path','release_date',
            'runtime','vote_average','vote_count','genres',
            'tfidf_vector','tfidf_norm','pop_score'
            )
        )
        max_pop = max(m['pop_score'] for m in raw_candidates) or 1.0

        scored = []
        # --- 3) Score each candidate ---
        for m in raw_candidates:
            # a) watchlist similarity: max cosine over all watch seeds
            watch_sim = 0.0
            for s in watch_seeds:
                dot = sum(s['tfidf_vector'].get(t,0)*w
                        for t,w in m['tfidf_vector'].items())
                denom = (s['tfidf_norm']*m['tfidf_norm']) or 1.0
                watch_sim = max(watch_sim, dot/denom)

            # b) search history similarity
            search_sim = 0.0
            for s in search_seeds:
                dot = sum(s['tfidf_vector'].get(t,0)*w
                        for t,w in m['tfidf_vector'].items())
                denom = (s['tfidf_norm']*m['tfidf_norm']) or 1.0
                search_sim = max(search_sim, dot/denom)

            # c) preference match (fraction of overlap in genres)
            movie_genres = set(m['genres'].split('|'))
            if pref_set:
                pref_match = len(movie_genres & pref_set) / len(pref_set)
            else:
                pref_match = 0.0

            # d) normalized popularity
            pop_norm = m['pop_score'] / max_pop

            # e) final blend
            final = (
                W_WATCH  * watch_sim
            + W_SEARCH * search_sim
            + W_PREF   * pref_match
            + W_POP    * pop_norm
            )
            m['_final'] = final
            scored.append(m)

        # sort descending
        scored.sort(key=lambda x: x['_final'], reverse=True)

        # exclude already watched
        watched_set = set(watch_ids)
        scored = [m for m in scored if m['tmdb_id'] not in watched_set]

        cache.set(cache_key, scored, CACHE_TTL)

    # --- 4) Paginate and render ---
    paginator = Paginator(scored, PAGE_SIZE)
    page_obj  = paginator.get_page(request.GET.get('page',1))
    movies    = list(page_obj.object_list)
    random.shuffle(movies)
    for m in movies:
        m['genres_list'] = [g for g in m['genres'].split('|') if g]

    # build pages window (1–3 only for demo)
    total, cur = paginator.num_pages, page_obj.number
    pages = list(range(1, min(total,3)+1))

    return render(request, 'user_profile/recommendations.html', {
        'movies':       movies,
        'page_obj':     page_obj,
        'pages_to_show':pages,
    })


def logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    return redirect('login')



    