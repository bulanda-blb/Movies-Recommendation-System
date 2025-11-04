from django.db import models
from django.db.models import Max
from django.conf import settings

class movie_user(models.Model):
    user_id = models.IntegerField(primary_key=True)
    email = models.EmailField(unique=True, max_length=255)
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    notification_on = models.BooleanField(default=False)
    join_time = models.DateTimeField()
    login_ip = models.GenericIPAddressField(null=True, blank=True)
    terms_check = models.BooleanField(default=False)

    class Meta:
        db_table = 'user_db'

    def save(self, *args, **kwargs):
        # auto-increment starting from 1000
        if not self.user_id:
            last = movie_user.objects.aggregate(max_id=Max('user_id'))['max_id']
            self.user_id = (last + 1) if last and last >= 1000 else 1000
        super().save(*args, **kwargs)


class Preference(models.Model):
    LENGTH_CHOICES = [
        ('<90', '< 90 min'),
        ('90-120', '90–120 min'),
        ('>120', '> 120 min'),
    ]
    CONTEXT_CHOICES = [
        ('Alone', 'Alone'),
        ('Family', 'With Family'),
        ('Friends', 'With Friends'),
    ]
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    user = models.OneToOneField(movie_user, on_delete=models.CASCADE)
    genres           = models.JSONField(default=list, blank=True)
    moods            = models.JSONField(default=list, blank=True)
    preferred_length = models.CharField(max_length=10, choices=LENGTH_CHOICES, blank=True)
    context          = models.CharField(max_length=10, choices=CONTEXT_CHOICES, blank=True)
    frequency        = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, blank=True)
    subtitles        = models.BooleanField(default=False)
    era              = models.JSONField(default=list, blank=True)
    content_type     = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"Prefs for user {self.user.user_id}"
