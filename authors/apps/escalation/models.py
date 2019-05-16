from django.db import models
from django.contrib.auth import get_user_model

from authors.apps.articles.models import Article


User = get_user_model()


class EscalationModel(models.Model):
    """
    Cases for escalation of an article
    """
    EXCALATION_CHOICES = (
        ('Plagiarism',
         'Reusing content without attribution (link and blockquotes)'),
        ('Rule Violation', 'Violates terms of agreement'),
        ('Spam', 'Creating multiple articles')

    )

    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=255, choices=EXCALATION_CHOICES)
    description = models.CharField(max_length=128)

    class Meta:
        ordering = ['timestamp', ]

    def get_articles_details(self):
        """
        Get all relevant articles details
        """
        return {
            "slug": self.article.slug,
            "title": self.article.title,
            "description": self.article.description,
            "body": self.article.body,
            "created_at": self.article.created_at,
            "updated_at": self.article.updated_at
        }
