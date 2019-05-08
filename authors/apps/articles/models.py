from django.db import models
from django.contrib.auth import get_user_model
from autoslug import AutoSlugField
from cloudinary.models import CloudinaryField
from cloudinary import CloudinaryImage

from vote.models import VoteModel

from authors.apps.profiles.models import Profile
import json

User = get_user_model()


class Tag(models.Model):
    """
    Model for for tags
    """
    tag_name = models.CharField(max_length=100)

    class Meta:
        ordering = ('tag_name',)

    def __str__(self):
        return self.tag_name

    @property
    def articles(self):
        """
        gets all articles associated with the tag
        """
        queryset = Article.objects.filter(tags__pk=self.pk)
        return queryset


class Article(VoteModel, models.Model):
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
    image = CloudinaryField('image')
    tags = models.ManyToManyField(Tag)
    favorited = models.BooleanField(default=False)
    favoritesCount = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['created_at', ]

    def get_image(self):
        """
        Retrieve article image
        """
        image_url = CloudinaryImage(str(self.image)).build_url(crop='fill')
        return image_url

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

    @property
    def tagList(self):
        """
        Gets all tags on an article
        """
        tags = [tag.tag_name for tag in self.tags.all()]
        return tags

    def clear_tags(self):
        """
        Clears all tags for an article
        """
        for tag in self.tags.all():
            self.tags.remove(tag)
            if not tag.articles:
                tag.delete()
        [self.tags.remove(tag) for tag in self.tags.all()]

    def get_favorited(self):
        favorite = self.favorited
        favorite = True
        return favorite


class Favorite(models.Model):
    """
    A class model for storing user fovorites and articles
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)


class RatingModel(models.Model):
    """
    Models for rating an article (0 - 5)
    """
    article = models.ForeignKey(
        Article, related_name='rated_article', on_delete=models.CASCADE)
    rated_by = models.ForeignKey(
        User, related_name='rated_by', on_delete=models.CASCADE)
    rate = models.IntegerField(default=0)

    def get_articles_details(self):
        """
        Fetch relevant articles details
        """
        return {
            "slug": self.article.slug,
            "title": self.article.title,
            "description": self.article.description,
            "body": self.article.body,
            "created_at": self.article.created_at,
            "updated_at": self.article.updated_at
        }
