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

    if not followers:
        return
    for user in followers:

        url = reverse(
            "articles:articles", args=[instance.slug])
        url = f"{settings.DOMAIN}{url}"
        notify.send(
            article_author,
            recipient=user.user,
            description="{} posted an article '{}' on {}".format(
                article_author,
                title.upper(),
                instance.created_at.strftime('%d-%B-%Y %H:%M')),
            verb=verbs.ARTICLE_CREATION,
            action_object=instance,
            resource_url=url
        )


def create_email_notification_handler(sender, instance, created, **kwargs):
    """
    notification handler for emails.
    """
    user = instance.recipient
    recipient = User.objects.get(email=user)
    send = recipient.notification_preferences.email_notifications_subscription
    if send is False:
        return
    description = instance.description
    instance.emailed = True
    token, created = Token.objects.get_or_create(user=user)
    if not created:
        token.created = timezone.now()
        token.save()
    url = reverse(
        "notifications:opt_out_link", args=[token])
    opt_out_link = f'{settings.DOMAIN}{url}'
    try:
        resource_url = instance.data['resource_url']
    except TypeError:
        resource_url = f"{settings.DOMAIN}/api/articles"

    html_content = render_to_string('notification_template.html', context={
        "opt_out_link": opt_out_link,
        "username": recipient.username,
        "description": description,
        "resource_url": resource_url
    })
    send_mail(
        "User Notification",
        '',
        settings.EMAIL_HOST_USER,
        [recipient.email],
        html_message=html_content)


def comment_handler(sender, instance, created, **kwargs):
    """
    notification handler for comments
    """
    recipients = []
    comment_author = instance.author
    article = instance.article
    favourited = Favorite.objects.filter(article=article)
    for user in favourited:
        email = user.user
        recipients.append(email)
    description_string = "{} posted a comment to {} on {}"
    url = reverse(
        "articles:articles", args=[article.slug])
    resource_url = f"{settings.DOMAIN}{url}"

    notify.send(comment_author,
                recipient=recipients,
                description=description_string.format(
                    comment_author.username,
                    article.title,
                    instance.created_at.strftime('%d-%B-%Y %H:%M')),
                target=article or instance,
                verb=verbs.COMMENT_CREATED,
                action_object=instance,
                resource_url=resource_url
                )


post_save.connect(create_email_notification_handler, sender=Notification)
post_save.connect(create_article_handler, sender=Article)
post_save.connect(comment_handler, sender=Comment)
