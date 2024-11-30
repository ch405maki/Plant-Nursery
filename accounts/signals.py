from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create a Profile for the new User, only if one doesn't already exist
        Profile.objects.get_or_create(user=instance)
    else:
        # Update the Profile for the existing User
        if instance.profile:
            instance.profile.save()
