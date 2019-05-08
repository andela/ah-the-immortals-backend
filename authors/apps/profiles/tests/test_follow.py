import json
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from ...authentication.models import User


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
        self.green = self.save_user(
            'green', 'green@gmail.com', 'passworddude')

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

    def get_user_object2(self, username='hulk',
                         email='hulk@gmail.com', password='passworddude'):
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
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(res.content), {'profile': {
                         'message': 'You now follow Thanos'}})

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
                         'message': 'You cannot follow yourself'}})

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
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(res.content), {'profile': {
                         'message': 'You have unfollowed Thanos'}})

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
                         'message': 'You already follow Thanos'}})

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
                         'message': 'You do not follow flex'}})

    def test_no_followers_yet(self):
        """test if user has any followers"""
        correct_user = self.get_user_object()
        jwt = correct_user.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + jwt)
        res = self.client.get('/api/profiles/jane/followers/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(res.content), {
                         'profile': {'followers': [], 'count': 0}})

    def test_no_followings_yet(self):
        """test if user has any followings"""
        correct_user = self.get_user_object()
        jwt = correct_user.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + jwt)
        res = self.client.get('/api/profiles/jane/follow/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(res.content), {
                         'profile': {'following': [], 'count': 0}})

    def test_get_all_following(self):
        correct_user = self.get_user_object()
        jwt = correct_user.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + jwt)

        res = self.client.get('/api/profiles/ironman/follow/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_all_followers(self):
        correct_user = self.get_user_object2()
        jwt = correct_user.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + jwt)

        res = self.client.get('/api/profiles/hulk/followers/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_user_not_found_follow(self):
        """test user not found when follow"""
        correct_user = self.get_user_object()
        jwt = correct_user.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + jwt)
        res = self.client.post(
            '/api/profiles/john/follow/')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(res.content), {'profile': {
                         'detail': 'User with that username Not found'}})

    def test_user_not_found_unfollow(self):
        """test user not found when unfollow"""
        correct_user = self.get_user_object()
        jwt = correct_user.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + jwt)
        res = self.client.delete(
            '/api/profiles/john/follow/')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(res.content), {'profile': {
                         'detail': 'User with that username Not found'}})

    def test_user_not_found_get_followers(self):
        """test user not found when getfollowers"""
        correct_user = self.get_user_object()
        jwt = correct_user.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + jwt)

        res = self.client.get('/api/profiles/john/followers/')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(res.content), {'profile': {
                         'detail': 'User with that username Not found'}})

    def test_user_not_found_get_followings(self):
        """test user not found when getfollowings"""
        correct_user = self.get_user_object()
        jwt = correct_user.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + jwt)

        res = self.client.get('/api/profiles/john/follow/')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json.loads(res.content), {'profile': {
                         'detail': 'User with that username Not found'}})

    def test_get_all_followers_with_response_message(self):
        correct_user = self.green
        jwt = correct_user.token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + jwt)

        res = self.client.get('/api/profiles/jane/followers/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(res.content), {
                         'profile': {'count': 0, 'followers': []}})
