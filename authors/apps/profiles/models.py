from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from cloudinary.models import CloudinaryField
from cloudinary import CloudinaryImage

User = get_user_model()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    image = CloudinaryField(
        'image', default='https://res.cloudinary.com/grean/image/upload/v1556488518/samples/vbioaj1wwewmtmeryucv.jpg')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at', ]

    def __str__(self):
        return self.user.username

    @property
    def fetch_username(self):
        """
        property method to fetch username
        """
        return self.user.username

    @property
    def fetch_image(self):
        """
        property method to fetch image
        """
        img_url = CloudinaryImage(str(self.image)).build_url(
            width=80, height=120, crop='fill')
        return img_url


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Followers(models.Model):
    """Model definition for Followers."""

    profile = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="w_following")
    followed = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="w_followed")

    class Meta:
        """Meta definition for Followers."""

        verbose_name = "Followers"
        verbose_name_plural = "Followers"

    def __str__(self):
        """Unicode representation of Followers."""
        return str(self.id)
