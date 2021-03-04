from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.exceptions import ErrorDetail
from beer_app.models import Beer, BeerReview, BeerRecommendation
from django.contrib.auth.models import User


class SignUpTests(APITestCase):
    # @classmethod
    # def setUpTestData(cls):
    #     """
    #     Create beer objects for mandatory user recommendation 
    #     """
    #     for i in range(1, 11):
    #         _ = Beer.objects.create(beer_name='Test Beer {}'.format(i), 
    #                                 beer_style='Iconic test beer', 
    #                                 brewery_name='Test brewery', 
    #                                 beer_abv='5.0')

    def test_create_valid_account(self):
        """
        Ensure we can create a new valid User object.
        """
        user_counts = User.objects.count()
        url = '/registration'
        data = {'email': 'test@user.com', 'password': 'test_password'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {'email': 'test@user.com'})
        self.assertEqual(User.objects.count(), user_counts + 1)
        self.assertEqual(User.objects.latest('id').email, 'test@user.com')

    def test_create_account_with_invalid_email(self):
        """
        Test attempt to register User with invalid email. 
        """
        user_counts = User.objects.count()
        url = '/registration'
        data = {'email': 'testuser.com', 'password': 'test_password'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # TODO: try to bypass implicit ErrorDetail instansiation
        self.assertEqual(response.data, {'email': [ErrorDetail('Enter a valid email address.', code='invalid')]})
        self.assertEqual(User.objects.count(), user_counts)
        self.assertNotEqual(User.objects.latest('id').email, 'testuser.com')

    def test_create_account_without_data(self):
        """
        Test attempt to register User without data in request body.
        """
        user_counts = User.objects.count()
        url = '/registration'
        data = {'email': '', 'password': ''}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # TODO: try to bypass implicit ErrorDetail instansiation
        self.assertEqual(response.data, {
                                            'email': [ErrorDetail('This field may not be blank.', code='blank')], 
                                            'password': [ErrorDetail('This field may not be blank.', code='blank')]
                                        })
        self.assertEqual(User.objects.count(), user_counts)

    def test_create_account_with_same_email(self):
        """
        Test attempt to register User with already exist email.
        """
        url = '/registration'
        data = {'email': 'test@user.com', 'password': 'test_password'}
        response = self.client.post(url, data, format='json')

        user_counts = User.objects.count()
        user_id = User.objects.latest('id').id
        url = '/registration'
        data = {'email': 'test@user.com', 'password': 'test_password_new'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # TODO: try to bypass implicit ErrorDetail instansiation
        self.assertEqual(response.data, {'email': [ErrorDetail('This field must be unique.', code='unique')]})
        self.assertEqual(User.objects.count(), user_counts)
        self.assertEqual(User.objects.latest('id').id, user_id)
