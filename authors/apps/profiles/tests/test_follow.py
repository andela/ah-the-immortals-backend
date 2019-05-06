import json
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from ...authentication.models import User
from ..models import Followers


class TestFollowUsers(APITestCase):
    """test class for FollowUsers"""

    def setUp(self):
        self.client = APIClient()
        self.flex = self.save_user(
            'flex', 'flex@gmail.com', 'passworddude')
        self.Thanos = self.save_user(
            'Thanos', 'Thanos@gmail.com', 'passworddude')
        self.jane = self.save_user(
            'jane', 'jane@gmail.com', 'passworddude')
        self.juma = self.save_user(
            'juma', 'juma@gmail.com', 'passworddude')

    def save_user(self, username, email, password):
        data = {'username': username,
                'email': email, 'password': password}
        res = User.objects.create_user(**data)
        res.is_verified = True
        res.save()
        return res

    def get_user_object(self, username='ironman',
                        email='ironman@gmail.com', password='passworddude'):
        user = self.save_user(username, email, password)
        return user

    def test_followed_Successfully(self):
        """test if user followed successfully"""
        correct_user = self.get_user_object()
        jwt = correct_user.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + jwt)
        res = self.client.post(
            '/api/profiles/Thanos/follow/')
        self.assertEqual(res.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(json.loads(res.content), {'profile': {
            'username': 'Thanos', 'first_name': '', 'last_name': '', 'bio': ''}})

    def test_cannot_followthemselves(self):
        """ test users cannot follow themselves"""
        correct_user = self.get_user_object()
        jwt = correct_user.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer  ' + jwt)
        res = self.client.post(
            '/api/profiles/{}/follow/'.format(correct_user.username))
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(res.content), {'profile': {
                         'error': 'You can not follow yourself.'}})

    def test_authenticated_user(self):
        """test if user is authenticated"""
        res = self.client.post('/api/profiles/flex/follow/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(json.loads(res.content), {'profile': {
            'detail': 'Authentication credentials were not provided.'}})

    def test_unfollow(self):
        """test user has unfollowed"""
        correct_user = self.get_user_object()
        jwt = correct_user.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + jwt)
        self.client.post('/api/profiles/Thanos/follow/')
        res = self.client.delete(
            '/api/profiles/Thanos/follow/')
        self.assertEqual(res.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(json.loads(res.content), {'profile': {
            'username': 'Thanos', 'first_name': '', 'last_name': '', 'bio': ''}})

    def test_already_following(self):
        """test if user is already following a user"""
        correct_user = self.get_user_object()
        jwt = correct_user.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + jwt)
        self.client.post('/api/profiles/Thanos/follow/')
        res = self.client.post(
            '/api/profiles/Thanos/follow/')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(res.content), {'profile': {
            'error': 'You are already following Thanos.'}})

    def test_cannot_unfollow_they_are_not_following(self):
        """test if a user is following before unfollowing"""
        correct_user = self.get_user_object()
        jwt = correct_user.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + jwt)
        res = self.client.delete(
            '/api/profiles/flex/follow/')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json.loads(res.content), {'profile': {
            'error': 'you have to be following the user in order to unfollow.'}})

    def test_no_followers_yet(self):
        """test if user has any followers"""
        correct_user = self.get_user_object()
        jwt = correct_user.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + jwt)
        res = self.client.get('/api/profiles/jane/followers/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(res.content), {'profile': {
            'message': 'jane has no followers yet'}})

    def test_no_followings_yet(self):
        """test if user has any followings"""
        correct_user = self.get_user_object()
        jwt = correct_user.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + jwt)
        res = self.client.get('/api/profiles/jane/follow/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(res.content), {'profile': {
            'message': 'jane has no followings yet'}})

    def test_get_all_following(self):
        correct_user = self.get_user_object()
        jwt = correct_user.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + jwt)
        follow = Followers()
        follow.profile_id = correct_user.pk
        follow.followed_id = self.flex.pk
        follow.save()

        res = self.client.get('/api/profiles/ironman/follow/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_all_followers(self):
        correct_user = self.get_user_object()
        jwt = correct_user.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + jwt)
        follow = Followers()
        follow.profile_id = correct_user.pk
        follow.followed_id = self.jane.pk
        follow.save()

        res = self.client.get('/api/profiles/ironman/followers/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
