from celery import shared_task
from django.utils import timezone
from .models import Banned

@shared_task
def check_and_unban_users():
    now = timezone.now()
    expired_bans = Banned.objects.filter(till_blocked__lte=now)
    expired_bans.delete()