from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from notifications.models import Notification
from notifications.signals import notify
from rest_framework.authtoken.models import Token

from authors.apps.articles.models import Article, Comment, Favorite
from authors.apps.authentication.models import User

from . import actions as verbs


def create_article_handler(sender, instance, created, **kwargs):
    """
    notification handler for articles
    """
    title = instance.title
    article_author = instance.author.profile
    followers = article_author.followers_list()
    description = "{} posted an article '{}' on {}".format(
        article_author,
        title.upper(),
        instance.created_at.strftime('%d-%B-%Y %H:%M'))

    if not followers:
        return
    for user in followers:
        if user.user.notification_preferences.in_app_notifications:
            url = reverse(
                "articles:articles", args=[instance.slug])
            url = f"{settings.DOMAIN}{url}"
            notify.send(
                article_author,
                recipient=user.user,
                description=description,
                verb=verbs.ARTICLE_CREATION,
                action_object=instance,
                resource_url=url
            )
        if user.user.notification_preferences.email_notifications:
            email_notification_handler(user, description)


def comment_handler(sender, instance, created, **kwargs):
    """
    notification handler for comments
    """
    recipients = []
    comment_author = instance.author
    article = instance.article
    favourited = Favorite.objects.filter(article=article)
    description = "{} posted a comment to {} on {}".format(
        comment_author.username,
        article.title,
        instance.created_at.strftime('%d-%B-%Y %H:%M'))
    url = reverse(
        "articles:articles", args=[article.slug])
    resource_url = f"{settings.DOMAIN}{url}"
    for user in favourited:
        email = user.user
        recipients.append(email)

        if email.notification_preferences.in_app_notifications:
            notify.send(comment_author,
                        recipient=recipients,
                        description=description,
                        target=article or instance,
                        verb=verbs.COMMENT_CREATED,
                        action_object=instance,
                        resource_url=resource_url
                        )
        if email.notification_preferences.email_notifications:
            email_notification_handler(user, description)


def email_notification_handler(user, description):
    token, created = Token.objects.get_or_create(user=user.user)
    if not created:
        token.created = timezone.now()
        token.save()
    url = reverse(
        "notifications:opt_out_link", args=[token])
    opt_out_link = f'{settings.DOMAIN}{url}'
    resource_url = url = f"{settings.DOMAIN}{url}"

    html_content = render_to_string(
        'notification_template.html', context={
            "opt_out_link": opt_out_link,
            "username": user.user.username,
            "description": description,
            "resource_url": resource_url
        })
    send_mail(
        "User Notification",
        '',
        settings.EMAIL_HOST_USER,
        [user.user.email],
        html_message=html_content)


post_save.connect(create_article_handler, sender=Article)
post_save.connect(comment_handler, sender=Comment)
