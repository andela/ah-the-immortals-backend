from django.db import models
from django.contrib.auth import get_user_model
from autoslug import AutoSlugField

from cloudinary.models import CloudinaryField
from cloudinary import CloudinaryImage

from authors.apps.profiles.models import Profile
from django.contrib.auth import get_user_model
User = get_user_model()


class Article(models.Model):
    """
    Model for articles
    """
    slug = AutoSlugField(populate_from='title', always_update=True,
                         blank=True, null=True, unique=True)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image = CloudinaryField(
        'image', default='https://res.cloudinary.com/grean/image/upload/v1556488518/samples/vbioaj1wwewmtmeryucv.jpg')

    def __str__(self):
        return self.slug, self.author.username

    class Meta:
        ordering = ['created_at', ]

    def get_image(self):
        """
        Retrieve article image
        """
        image_url = CloudinaryImage(str(self.image)).build_url(crop='fill')
        return image_url

    def get_absolute_url(self):
        """
        Defines the main url to prevent duplicate content
        """
        return "authors:articles", (self.slug)

    def get_author_details(self):
        """
        Fetch author's Profile
        """
        return {
            "username": self.author.username,
            "bio": self.author.profile.bio,
            "image": self.author.profile.fetch_image,
            "following": self.author.profile.following.reverse
        }
