from django.db import models
from django.contrib.auth import get_user_model
from authors.apps.profiles.models import Profile
from authors.apps.articles.models import Article
from .utils import retrieve_word, check_field

User = get_user_model()


class Highlight(models.Model):
    """
    Models for highlight feature
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    field = models.CharField(max_length=30)
    comment = models.TextField(null=True, blank=True)
    start_index = models.IntegerField(null=False, blank=False)
    end_index = models.IntegerField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('start_index',)

    def user_details(self):
        """
        Retrieve user details
        """
        return {
            "username": self.user.username,
            "image": self.user.profile.fetch_image
        }

    def article_details(self):
        """
        Retrieve article details
        """
        return self.article.slug

    def get_highlighted_text(self):
        """
        Retrieve highlighted text from the article
        """
        field_data = check_field(self.article, self.field)
        text = retrieve_word(field_data, self.start_index, self.end_index)
        return text
