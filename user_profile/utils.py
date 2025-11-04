# user_profile/utils.py

from authentication.models import Preference

def build_preference_set(user_id):
    try:
        prefs = Preference.objects.get(user_id=user_id)
        return set(prefs.genres or [])
    except Preference.DoesNotExist:
        return set()
