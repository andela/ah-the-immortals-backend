from django_social_share.templatetags import social_share


def twitter_share_url(context, article_uri, title):
    return social_share.post_to_twitter(
        context,
        text=title,
        obj_or_url=article_uri
    )['tweet_url']


def facebook_share_url(context, article_uri, title):
    return social_share.post_to_facebook(
        context,
        obj_or_url=article_uri
    )['facebook_url']


def email_share_url(context, article_uri, title):
    text = title
    return social_share.send_email_url(
        context,
        text,
        article_uri
    )['mailto_url']


def linkedin_share_url(context, article_uri, title):
    return social_share.post_to_linkedin(
        context,
        title,
        article_uri
    )['linkedin_url']


def reddit_share_url(context, article_uri, title):
    return social_share.post_to_reddit(
        context,
        title=title,
        obj_or_url=article_uri
    )['reddit_url']


def telegram_share_url(context, article_uri, title):
    return social_share.post_to_telegram(
        context,
        title=title,
        obj_or_url=article_uri
    )['telegram_url']


def generate_share_url(context, provider, article, article_uri):
    title = '{} by {}\n'.format(article.title, article.author.username)

    providers = {
        'twitter': twitter_share_url(
            context, article_uri, title),
        'facebook': facebook_share_url(
            context, article_uri, title),
        'email': email_share_url(
            context, article_uri, title),
        'linkedin': linkedin_share_url(
            context, article_uri, title),
        'reddit': reddit_share_url(
            context, article_uri, title),
        'telegram': telegram_share_url(
            context, article_uri, title)
    }

    return providers[provider]
