from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# this class was written with help as a placeholder - come back to understand and edit it 
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # do we need username and name field? does that pull from database? 
    bio = models.TextField(max_length=400, blank=True)
    city = models.TextField(max_length=40, blank=True)
    profile_picture = models.ImageField(upload_to='profile_photos', blank=True, null=True)
    header_photo = models.ImageField(upload_to='header_photos', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)