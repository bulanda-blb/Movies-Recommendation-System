from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Watchlist, SearchHistory
from authentication.models import Preference

# whenever a user’s data changes, clear their recs
def _clear_cache_for(user_id):
    cache.delete(f"user_recs_{user_id}")

@receiver(post_save, sender=Watchlist)
@receiver(post_delete, sender=Watchlist)
def watchlist_changed(sender, instance, **kwargs):
    _clear_cache_for(instance.user.user_id)

@receiver(post_save, sender=SearchHistory)
@receiver(post_delete, sender=SearchHistory)
def searchhistory_changed(sender, instance, **kwargs):
    _clear_cache_for(instance.user.user_id)

@receiver(post_save, sender=Preference)
@receiver(post_delete, sender=Preference)
def preferences_changed(sender, instance, **kwargs):
    _clear_cache_for(instance.user.user_id)
