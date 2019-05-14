from .basetests import BaseTest
from rest_framework import status
from rest_framework.reverse import reverse


class TestSocialShare(BaseTest):
    """
    Class to test returning of social links during sharing
    """
    facebook_share_url = reverse("articles:share", args=[
                                 "this-is-mine", "facebook"])
    twitter_share_url = reverse("articles:share", args=[
                                "this-is-mine", "twitter"])
    telegram_share_url = reverse("articles:share", args=[
                                 "this-is-mine", "telegram"])
    reddit_share_url = reverse("articles:share", args=[
                               "this-is-mine", "reddit"])
    email_share_url = reverse("articles:share", args=["this-is-mine", "email"])
    linkedin_share_url = reverse("articles:share", args=[
                                 "this-is-mine", "linkedin"])
    invalid_provider_url = reverse("articles:share", args=[
                                   "this-is-mine", "fghjhg"])

    def test_facebook_share(self):
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        response = self.client.get(self.facebook_share_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['share']['provider'], 'facebook')
        self.assertTrue(response.data['share']['link'])

    def test_twitter_share(self):
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        response = self.client.get(self.twitter_share_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['share']['provider'], 'twitter')
        self.assertTrue(response.data['share']['link'])

    def test_telegram_share(self):
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        response = self.client.get(self.telegram_share_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['share']['provider'], 'telegram')
        self.assertTrue(response.data['share']['link'])

    def test_reddit_share(self):
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        response = self.client.get(self.reddit_share_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['share']['provider'], 'reddit')
        self.assertTrue(response.data['share']['link'])

    def test_email_share(self):
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        response = self.client.get(self.email_share_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['share']['provider'], 'email')
        self.assertTrue(response.data['share']['link'])

    def test_linkedin_share(self):
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        response = self.client.get(self.linkedin_share_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['share']['provider'], 'linkedin')
        self.assertTrue(response.data['share']['link'])

    def test_invalid_provider_share(self):
        self.is_authenticated("adam@gmail.com", "@Us3r.com")
        response = self.client.get(self.invalid_provider_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'],
                         'Please select a valid provider - '
                         'twitter, facebook, email, telegram, '
                         'linkedin, reddit')
