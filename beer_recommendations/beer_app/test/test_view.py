from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.exceptions import ErrorDetail
from rest_framework.authtoken.models import Token
from beer_app.models import Beer, BeerReview, BeerRecommendation
from django.contrib.auth.models import User
from django.conf import settings
from decimal import Decimal
import math


NUMBER_NEXT_PAGES_TO_CHECK = 2


class BeerListViewTests(APITestCase):

    def test_get_beer_list_with_valid_token(self):
        """
        Ensure we can get beer list with valid token.
        """
        # test username
        test_user_name = 'stcules'
        # we can force authenticate user to bypass explicit token usage when we don't need to test it
        user = User.objects.get(username=test_user_name)
        self.client.force_authenticate(user=user)
        # url for request        
        url = '/beer'
        # get request to url 
        response = self.client.get(url, format='json')
        # test assertions below
        # assert status code equal 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_beer_list_with_invalid_credentials(self):
        # mannually add invalid credentials to all requests from client 
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format('invalid_test'))
        # url for request        
        url = '/beer'
        # get request to url 
        response = self.client.get(url, format='json')
        # test assertions below
        # assert status code equal 401
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # assert that data contains message about invalid token
        # ErrorDetail is error class that write errors to response data
        self.assertEqual(response.data, {'detail':  ErrorDetail(string='Invalid token.', code='authentication_failed')})

    def test_get_beer_list_without_credentials_header(self):
        # url for request        
        url = '/beer'
        # get request to url 
        response = self.client.get(url, format='json')
        # test assertions below
        # assert status code equal 401
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # assert that data contains message about invalid token
        self.assertEqual(response.data, {'detail': ErrorDetail(string='Authentication credentials were not provided.', code='not_authenticated')})

    def test_get_beer_list_returns_valid_data(self):
        # test username
        test_user_name = 'stcules'
        # we can force authenticate user to bypass explicit token usage when we don't need to test it
        user = User.objects.get(username=test_user_name)
        self.client.force_authenticate(user=user)
        # url for request  
        url = '/beer'
        # get request to url 
        response = self.client.get(url, format='json')
        # assert data field (containing dict) as you wish

        # assert that results contains only 10 elements (pagination) 
        # good practice is to use framework settings for this purpose (./beer_recommendations/settings.py)
        self.assertEqual(len(response.data['results']), settings.REST_FRAMEWORK['PAGE_SIZE'])
        # BeerList view sorts results by id so we can test that all ids are sorted
        all_page_ids = [beer_data['id'] for beer_data in response.data['results']]
        ids_iterator = iter(all_page_ids)
        _ = ids_iterator.__next__()
        self.assertTrue(all(prev_idx <= next_idx for prev_idx, next_idx in zip(all_page_ids, ids_iterator)))
        # test that beer result contains all required fields (they are presented in serializers classes)
        first_beer_data = response.data['results'][0]
        self.assertTrue('id' in first_beer_data)
        self.assertTrue('beer_name' in first_beer_data)
        self.assertTrue('beer_style' in first_beer_data)
        self.assertTrue('average_rate' in first_beer_data)
        self.assertTrue('beer_image' in first_beer_data)

    def test_get_beer_list_returns_valid_redirection_chains(self):
        # calculate number of pages
        num_pages = math.ceil(Beer.objects.count() / settings.REST_FRAMEWORK['PAGE_SIZE'])
        # test username
        test_user_name = 'stcules'
        # we can force authenticate user to bypass explicit token usage
        user = User.objects.get(username=test_user_name)
        self.client.force_authenticate(user=user)
        # url for request  
        url = '/beer'
        # get request to url with following all redirections 
        response = self.client.get(url, format='json')
        # assert that response data hasn't refer to previous page (as it's first page) 
        self.assertTrue(response.data['previous'] is None)
        # assert that response data has refer to next page (is not None) if number of pages is more than 1 
        has_next = num_pages > 1 
        self.assertEqual(response.data['next'] is not None, has_next)

        # check redirection to next page
        visited_pages = 1
        while visited_pages <= NUMBER_NEXT_PAGES_TO_CHECK and visited_pages <= num_pages:
            next_url = response.data['next']
            if next_url is not None:
                response = self.client.get(next_url, format='json')
                visited_pages += 1
                self.assertTrue(response.data['previous'] is not None)
            else:
                break

        url = '/beer?page={}'.format(num_pages)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # assert that response data isn't refer to next page (is None) 
        self.assertTrue(response.data['next'] is None)

    def test_get_beer_list_with_filters(self):
        # calculate number of pages
        num_beers = Beer.objects.all().filter(beer_name__icontains='Light').filter(beer_style__icontains='Lager').count()
        # test username
        test_user_name = 'stcules'
        # we can force authenticate user to bypass explicit token usage
        user = User.objects.get(username=test_user_name)
        self.client.force_authenticate(user=user)
        # url for request  
        url = '/beer?beer_style=Lager&beer_name=Light'
        # get request to url with following all redirections 
        response = self.client.get(url, format='json')
        # assert that response data count is equal to true count after filtering 
        self.assertEqual(response.data['count'], num_beers)


class BeerDetailViewTests(APITestCase):
    
    def test_get_beer_detail_with_valid_token(self):
        """
        Ensure we can get beer detail with valid token.
        """
        # test username
        test_user_name = 'stcules'
        # we can force authenticate user to bypass explicit token usage when we don't need to test it
        user = User.objects.get(username=test_user_name)
        self.client.force_authenticate(user=user)
        # url for request        
        url = '/beer/100'
        # get request to url 
        response = self.client.get(url, format='json')
        # test assertions below
        # assert status code equal 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_beer_detail_with_invalid_token(self):
        # mannually add invalid credentials to all requests from client 
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format('invalid_test'))
        # url for request        
        url = '/beer/100'
        # get request to url 
        response = self.client.get(url, format='json')
        # assert status code equal 401
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # assert that data contains message about invalid token
        # ErrorDetail is error class that write errors to response data
        self.assertEqual(response.data, {'detail':  ErrorDetail(string='Invalid token.', code='authentication_failed')})

    def test_get_beer_detail_without_token_header(self):
        # url for request        
        url = '/beer/100'
        # get request to url 
        response = self.client.get(url, format='json')
        # assert status code equal 401
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # assert that data contains message about not provided credentials
        self.assertEqual(response.data, {'detail': ErrorDetail(string='Authentication credentials were not provided.', code='not_authenticated')})
    
    def test_get_beer_detail_returns_without_beer_id(self):
        # test username
        test_user_name = 'stcules'
        # we can force authenticate user to bypass explicit token usage when we don't need to test it
        user = User.objects.get(username=test_user_name)
        self.client.force_authenticate(user=user)
        # url for request  
        url = '/beer/'
        # get request to url 
        response = self.client.get(url, format='json')
        # test that status code equals 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_beer_detail_returns_valid_data_without_review_id(self):
        # test username
        test_user_name = 'stcules'
        # we can force authenticate user to bypass explicit token usage when we don't need to test it
        user = User.objects.get(username=test_user_name)
        self.client.force_authenticate(user=user)
        # url for request  
        url = '/beer/100'
        # get request to url 
        response = self.client.get(url, format='json')
        # test that beer detail contains valid information
        self.assertEqual(response.data['id'], 100)
        self.assertEqual(response.data['beer_name'], 'Wheat Ale')
        self.assertEqual(response.data['beer_style'], 'American Pale Wheat Ale')
        self.assertEqual(response.data['brewery_name'], 'Destiny Brewing Company')
        self.assertEqual(response.data['beer_abv'], Decimal('5.0'))
        self.assertEqual(response.data['average_rate'], Decimal('4.5'))
        self.assertEqual(response.data['average_aroma'], Decimal('3.0'))
        self.assertEqual(response.data['average_appearance'], Decimal('4.0'))
        self.assertEqual(response.data['average_palate'], Decimal('4.0'))
        self.assertEqual(response.data['average_taste'], Decimal('4.0'))
        self.assertTrue('/media/images.jpg' in response.data['beer_image'])
        self.assertEqual(response.data['is_reviewed'], None)

    def test_get_beer_detail_returns_valid_data_with_review_id(self):
        # test username
        test_user_name = 'stcules'
        # we can force authenticate user to bypass explicit token usage when we don't need to test it
        user = User.objects.get(username=test_user_name)
        self.client.force_authenticate(user=user)
        # url for request  
        url = '/beer/38567'
        # get request to url 
        response = self.client.get(url, format='json')
        # test that beer detail contains valid information
        self.assertEqual(response.data['id'], 38567)
        self.assertEqual(response.data['beer_name'], 'Karlsberg Black Baron')
        self.assertEqual(response.data['beer_style'], 'Schwarzbier')
        self.assertEqual(response.data['brewery_name'], 'Karlsberg Brauerei')
        self.assertEqual(response.data['beer_abv'], Decimal('4.9'))
        self.assertEqual(response.data['average_rate'], Decimal('3.0'))
        self.assertEqual(response.data['average_aroma'], Decimal('2.5'))
        self.assertEqual(response.data['average_appearance'], Decimal('3.0'))
        self.assertEqual(response.data['average_palate'], Decimal('2.5'))
        self.assertEqual(response.data['average_taste'], Decimal('2.8'))
        self.assertTrue('/media/images.jpg' in response.data['beer_image'])
        self.assertEqual(response.data['is_reviewed'], 973423)


class BeerRatingsViewTests(APITestCase):
    
    def test_get_beer_ratings_with_valid_token(self):
        """
        Ensure we can get beer rates with valid token.
        """
        # test username
        test_user_name = 'stcules'
        # we can force authenticate user to bypass explicit token usage when we don't need to test it
        user = User.objects.get(username=test_user_name)
        self.client.force_authenticate(user=user)
        # url for request        
        url = '/beer_rates'
        # get request to url 
        response = self.client.get(url, format='json')
        # assert status code equal 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        num_beers = Beer.objects.all().count()
        self.assertEqual(len(response.data['results']), settings.REST_FRAMEWORK['PAGE_SIZE'])
        self.assertEqual(response.data['count'], num_beers)
        self.assertEqual(response.data['results'][0]['average_rate'], Decimal('5.0'))
        # assert all required data in object:
        self.assertTrue('id' in response.data['results'][0])
        self.assertTrue('beer_name' in response.data['results'][0])
        self.assertTrue('beer_style' in response.data['results'][0])
        self.assertTrue('brewery_name' in response.data['results'][0])
        self.assertTrue('beer_abv' in response.data['results'][0])
        self.assertTrue('average_rate' in response.data['results'][0])
        self.assertTrue('beer_image' in response.data['results'][0])

    def test_get_beer_rates_with_invalid_token(self):
        # mannually add invalid credentials to all requests from client 
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format('invalid_test'))
        # url for request        
        url = '/beer_rates'
        # get request to url 
        response = self.client.get(url, format='json')
        # assert status code equal 401
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # assert that data contains message about invalid token
        # ErrorDetail is error class that write errors to response data
        self.assertEqual(response.data, {'detail':  ErrorDetail(string='Invalid token.', code='authentication_failed')})

    def test_get_beer_list_without_token_header(self):
        # url for request        
        url = '/beer_rates'
        # get request to url 
        response = self.client.get(url, format='json')
        # assert status code equal 401
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # assert that data contains message about not provided credentials
        self.assertEqual(response.data, {'detail': ErrorDetail(string='Authentication credentials were not provided.', code='not_authenticated')})

    def test_get_beer_list_returns_valid_redirection_chains(self):
        # calculate number of pages
        num_pages = math.ceil(Beer.objects.count() / settings.REST_FRAMEWORK['PAGE_SIZE'])
        # test username
        test_user_name = 'stcules'
        # we can force authenticate user to bypass explicit token usage
        user = User.objects.get(username=test_user_name)
        self.client.force_authenticate(user=user)
        # url for request  
        url = '/beer_rates'
        # get request to url with following all redirections 
        response = self.client.get(url, format='json')
        # assert that response data hasn't refer to previous page (as it's first page) 
        self.assertTrue(response.data['previous'] is None)
        # assert that response data has refer to next page (is not None) if number of pages is more than 1 
        has_next = num_pages > 1 
        self.assertEqual(response.data['next'] is not None, has_next)

        # check redirection to next page
        visited_pages = 1
        while visited_pages <= NUMBER_NEXT_PAGES_TO_CHECK and visited_pages <= num_pages:
            next_url = response.data['next']
            if next_url is not None:
                response = self.client.get(next_url, format='json')
                visited_pages += 1
                self.assertTrue(response.data['previous'] is not None)
            else:
                break

        url = '/beer_rates?page={}'.format(num_pages)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # assert that response data isn't refer to next page (is None) 
        self.assertTrue(response.data['next'] is None)
        self.assertTrue(response.data['previous'] is not None)


class BeerReviewListViewTests(APITestCase):

    def test_get_beer_review_list_with_valid_token(self):
        """
        Ensure we can get beer reviews list with valid token.
        """
        # test username
        test_user_name = 'stcules'
        # we can force authenticate user to bypass explicit token usage when we don't need to test it
        user = User.objects.get(username=test_user_name)
        self.client.force_authenticate(user=user)
        # url for request        
        url = '/beer_review'
        # get request to url 
        response = self.client.get(url, format='json')
        # test assertions below
        # assert status code equal 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_beer_review_list_with_invalid_credentials(self):
        # mannually add invalid credentials to all requests from client 
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format('invalid_test'))
        # url for request        
        url = '/beer_review'
        # get request to url 
        response = self.client.get(url, format='json')
        # test assertions below
        # assert status code equal 401
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # assert that data contains message about invalid token
        # ErrorDetail is error class that write errors to response data
        self.assertEqual(response.data, {'detail':  ErrorDetail(string='Invalid token.', code='authentication_failed')})

    def test_get_beer_review_list_without_credentials_header(self):
        # url for request        
        url = '/beer_review'
        # get request to url 
        response = self.client.get(url, format='json')
        # test assertions below
        # assert status code equal 401
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # assert that data contains message about invalid token
        self.assertEqual(response.data, {'detail': ErrorDetail(string='Authentication credentials were not provided.', code='not_authenticated')})

    def test_get_beer_review_list_with_zero_review_user(self):
        url = '/registration'
        # data for request
        data = {'email': 'test@user.com', 'password': 'test_password'}
        # post request to url with data in json format 
        response = self.client.post(url, data, format='json')

        # test username
        test_user_name = 'test@user.com'
        # we can force authenticate user to bypass explicit token usage when we don't need to test it
        user = User.objects.get(username=test_user_name)
        self.client.force_authenticate(user=user)
        # url for request  
        url = '/beer_review'
        # get request to url 
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['results']), 0)

    def test_get_beer_review_list_with_many_reviews_user(self):
        # test username
        test_user_name = 'stcules'
        # we can force authenticate user to bypass explicit token usage when we don't need to test it
        user = User.objects.get(username=test_user_name)
        self.client.force_authenticate(user=user)
        # url for request  
        url = '/beer_review'
        # get request to url 
        response = self.client.get(url, format='json')
        # assert data field (containing dict) as you wish

        # assert that results contains only 10 elements (pagination) 
        # good practice is to use framework settings for this purpose (./beer_recommendations/settings.py)
        self.assertEqual(len(response.data['results']), settings.REST_FRAMEWORK['PAGE_SIZE'])
        self.assertEqual(response.data['count'], 1788)
        # test that beer result contains all required fields (they are presented in serializers classes)
        first_beer_data = response.data['results'][0]
        self.assertTrue('id' in first_beer_data)
        self.assertTrue('review_beer' in first_beer_data)
        self.assertTrue('review_time' in first_beer_data)
        self.assertTrue('beer_name' in first_beer_data)
        self.assertTrue('beer_style' in first_beer_data)
        self.assertTrue('beer_image' in first_beer_data)
        self.assertTrue('review_overall' in first_beer_data)

    def test_get_beer_review_list_returns_valid_redirection_chains(self):
        # test username
        test_user_name = 'stcules'
        user = User.objects.get(username=test_user_name)
        # calculate number of pages
        num_pages = math.ceil(BeerReview.objects.all().filter(review_user=user).count() / settings.REST_FRAMEWORK['PAGE_SIZE'])
        # we can force authenticate user to bypass explicit token usage
        self.client.force_authenticate(user=user)
        # url for request  
        url = '/beer_review'
        # get request to url with following all redirections 
        response = self.client.get(url, format='json')
        # assert that response data hasn't refer to previous page (as it's first page) 
        self.assertTrue(response.data['previous'] is None)
        # assert that response data has refer to next page (is not None) if number of pages is more than 1 
        has_next = num_pages > 1 
        self.assertEqual(response.data['next'] is not None, has_next)

        # check redirection to next page
        visited_pages = 1
        while visited_pages <= NUMBER_NEXT_PAGES_TO_CHECK and visited_pages <= num_pages:
            next_url = response.data['next']
            if next_url is not None:
                response = self.client.get(next_url, format='json')
                visited_pages += 1
                self.assertTrue(response.data['previous'] is not None)
            else:
                break

        url = '/beer_review?page={}'.format(num_pages)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # assert that response data isn't refer to next page (is None) 
        self.assertTrue(response.data['next'] is None)


class BeerReviewPostViewTests(APITestCase):
    
    def test_create_beer_review_with_valid_token(self):
        """
        Ensure we can create a beer review with valid token.
        """
        review_counts = BeerReview.objects.count()
        # test username
        test_user_name = 'stcules'
        # we can force authenticate user to bypass explicit token usage when we don't need to test it
        user = User.objects.get(username=test_user_name)
        self.client.force_authenticate(user=user)
        
        # test user hasn't reviewed such beer yet
        # url for request        
        url = '/beer/100'
        # get request to url 
        response = self.client.get(url, format='json')
        # test that beer detail contains valid information
        self.assertEqual(response.data['id'], 100)
        self.assertEqual(response.data['is_reviewed'], None)

        # url for request 
        url = '/beer_review_post'
        # data for request
        data = {'review_beer': 100, 
                'review_overall': 3.0,
                'review_aroma': 3,
                'review_appearance': 2,
                'review_palate': 4,
                'review_taste': 3}
        # post request to url with data in json format 
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BeerReview.objects.count(), review_counts + 1)
        self.assertEqual(BeerReview.objects.latest('id').review_beer.id, 100)
        self.assertEqual(BeerReview.objects.latest('id').review_overall, Decimal(3.0))
        self.assertEqual(BeerReview.objects.latest('id').review_aroma, Decimal(3.0))
        self.assertEqual(BeerReview.objects.latest('id').review_appearance, Decimal(2.0))
        self.assertEqual(BeerReview.objects.latest('id').review_palate, Decimal(4.0))
        self.assertEqual(BeerReview.objects.latest('id').review_taste, Decimal(3.0))

        url = '/beer/100'
        # get request to url 
        response = self.client.get(url, format='json')
        # test that beer detail contains valid information
        self.assertEqual(response.data['id'], 100)
        self.assertEqual(response.data['is_reviewed'], BeerReview.objects.latest('id').id)

    def test_create_beer_review_with_invalid_credentials(self):
        # mannually add invalid credentials to all requests from client 
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format('invalid_test'))
        # url for request        
        url = '/beer_review_post'
        # get request to url 
        response = self.client.post(url, format='json')
        # test assertions below
        # assert status code equal 401
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # assert that data contains message about invalid token
        # ErrorDetail is error class that write errors to response data
        self.assertEqual(response.data, {'detail':  ErrorDetail(string='Invalid token.', code='authentication_failed')})

    def test_create_beer_review_without_credentials_header(self):
        # url for request        
        url = '/beer_review_post'
        # get request to url 
        response = self.client.post(url, format='json')
        # test assertions below
        # assert status code equal 401
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # assert that data contains message about invalid token
        self.assertEqual(response.data, {'detail': ErrorDetail(string='Authentication credentials were not provided.', code='not_authenticated')})

    def test_create_beer_review_for_inexisted_beer(self):
        review_counts = BeerReview.objects.count()
        # test username
        test_user_name = 'stcules'
        # we can force authenticate user to bypass explicit token usage when we don't need to test it
        user = User.objects.get(username=test_user_name)
        self.client.force_authenticate(user=user)
        # url for request  
        url = '/beer_review_post'
        inexisted_beer_id = BeerReview.objects.latest('id').review_beer.id + 1
        data = {'review_beer': inexisted_beer_id, 
                'review_overall': 3.0,
                'review_aroma': 3,
                'review_appearance': 2,
                'review_palate': 4,
                'review_taste': 3}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # TODO: try to bypass implicit ErrorDetail instansiation
        self.assertEqual(response.data, {
                                            'review_beer': [ErrorDetail('Invalid pk \"{}\" - object does not exist.'.format(str(inexisted_beer_id)), 
                                                                        code='does_not_exist')], 
                                        })
        self.assertEqual(BeerReview.objects.count(), review_counts)

    def test_create_beer_review_with_invalid_data(self):
        review_counts = BeerReview.objects.count()
        # test username
        test_user_name = 'stcules'
        # we can force authenticate user to bypass explicit token usage when we don't need to test it
        user = User.objects.get(username=test_user_name)
        self.client.force_authenticate(user=user)
        # url for request  
        url = '/beer_review_post'
        data = {'review_beer': 'one hundred', 
                'review_overall': 'three.',
                'review_aroma': 'string',
                'review_appearance': 'two',
                'review_palate': 4.25,
                'review_taste': 'three'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # TODO: try to bypass implicit ErrorDetail instansiation
        self.assertEqual(response.data, {
                                            'review_beer': [ErrorDetail('Incorrect type. Expected pk value, received str.', code='incorrect_type')], 
                                            'review_overall': [ErrorDetail('A valid number is required.', code='invalid')],
                                            'review_aroma': [ErrorDetail('A valid integer is required.', code='invalid')], 
                                            'review_appearance': [ErrorDetail('A valid integer is required.', code='invalid')],
                                            'review_palate': [ErrorDetail('A valid integer is required.', code='invalid')], 
                                            'review_taste': [ErrorDetail('A valid integer is required.', code='invalid')]
                                        })
        self.assertEqual(BeerReview.objects.count(), review_counts)

    def test_create_beer_review_with_blank_fields(self):
        review_counts = BeerReview.objects.count()
        # test username
        test_user_name = 'stcules'
        # we can force authenticate user to bypass explicit token usage when we don't need to test it
        user = User.objects.get(username=test_user_name)
        self.client.force_authenticate(user=user)
        # url for request  
        url = '/beer_review_post'
        data = {'review_beer': None, 
                'review_overall': None,
                'review_aroma': None,
                'review_appearance': None,
                'review_palate': None,
                'review_taste': None}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # TODO: try to bypass implicit ErrorDetail instansiation
        self.assertEqual(response.data, {
                                            'review_beer': [ErrorDetail('This field may not be null.', code='null')], 
                                            'review_overall': [ErrorDetail('This field may not be null.', code='null')],
                                            'review_aroma': [ErrorDetail('This field may not be null.', code='null')], 
                                            'review_appearance': [ErrorDetail('This field may not be null.', code='null')],
                                            'review_palate': [ErrorDetail('This field may not be null.', code='null')], 
                                            'review_taste': [ErrorDetail('This field may not be null.', code='null')]
                                        })
        self.assertEqual(BeerReview.objects.count(), review_counts)

    def test_create_beer_review_without_fields(self):
        review_counts = BeerReview.objects.count()
        # test username
        test_user_name = 'stcules'
        # we can force authenticate user to bypass explicit token usage when we don't need to test it
        user = User.objects.get(username=test_user_name)
        self.client.force_authenticate(user=user)
        # url for request  
        url = '/beer_review_post'
        data = {'fake_string': 'fake_string'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # TODO: try to bypass implicit ErrorDetail instansiation
        self.assertEqual(response.data, {
                                            'review_beer': [ErrorDetail('This field is required.', code='required')], 
                                            'review_overall': [ErrorDetail('This field is required.', code='required')],
                                            'review_aroma': [ErrorDetail('This field is required.', code='required')], 
                                            'review_appearance': [ErrorDetail('This field is required.', code='required')],
                                            'review_palate': [ErrorDetail('This field is required.', code='required')], 
                                            'review_taste': [ErrorDetail('This field is required.', code='required')]
                                        })
        self.assertEqual(BeerReview.objects.count(), review_counts)


class BeerReviewPutViewTests(APITestCase):
    
    def test_update_beer_review_with_valid_token(self):
        """
        Ensure we can update a beer review with valid token.
        """
        review_counts = BeerReview.objects.count()
        # test username
        test_user_name = 'stcules'
        # we can force authenticate user to bypass explicit token usage when we don't need to test it
        user = User.objects.get(username=test_user_name)
        self.client.force_authenticate(user=user)
        
        # test user has reviewed such beer
        # url for request        
        url = '/beer/1'
        # get request to url 
        response = self.client.get(url, format='json')
        # test that beer detail contains valid information
        self.assertEqual(response.data['id'], 1)
        self.assertEqual(response.data['is_reviewed'], 1)

        # url for request 
        url = '/beer_review_put'
        # data for request
        data = {'id': 1,
                'review_beer': 1, 
                'review_overall': 3.0,
                'review_aroma': 3,
                'review_appearance': 2,
                'review_palate': 4,
                'review_taste': 3}
        # post request to url with data in json format 
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(BeerReview.objects.count(), review_counts)
        self.assertEqual(BeerReview.objects.get(id=1).review_beer.id, 1)
        self.assertEqual(BeerReview.objects.get(id=1).review_overall, Decimal(3.0))
        self.assertEqual(BeerReview.objects.get(id=1).review_aroma, Decimal(3.0))
        self.assertEqual(BeerReview.objects.get(id=1).review_appearance, Decimal(2.0))
        self.assertEqual(BeerReview.objects.get(id=1).review_palate, Decimal(4.0))
        self.assertEqual(BeerReview.objects.get(id=1).review_taste, Decimal(3.0))

    def test_update_beer_review_with_invalid_credentials(self):
        # mannually add invalid credentials to all requests from client 
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format('invalid_test'))
        # url for request        
        url = '/beer_review_put'
        # get request to url 
        response = self.client.put(url, format='json')
        # test assertions below
        # assert status code equal 401
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # assert that data contains message about invalid token
        # ErrorDetail is error class that write errors to response data
        self.assertEqual(response.data, {'detail':  ErrorDetail(string='Invalid token.', code='authentication_failed')})

    def test_update_beer_review_without_credentials_header(self):
        # url for request        
        url = '/beer_review_put'
        # get request to url 
        response = self.client.put(url, format='json')
        # test assertions below
        # assert status code equal 401
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # assert that data contains message about invalid token
        self.assertEqual(response.data, {'detail': ErrorDetail(string='Authentication credentials were not provided.', code='not_authenticated')})

    def test_update_beer_review_for_inexisted_review(self):
        review_counts = BeerReview.objects.count()
        # test username
        test_user_name = 'stcules'
        # we can force authenticate user to bypass explicit token usage when we don't need to test it
        user = User.objects.get(username=test_user_name)
        self.client.force_authenticate(user=user)
        # url for request  
        url = '/beer_review_put'
        inexisted_review_id = BeerReview.objects.latest('id').id + 1
        data = {'id': inexisted_review_id,
                'review_beer': 1, 
                'review_overall': 3.0,
                'review_aroma': 3,
                'review_appearance': 2,
                'review_palate': 4,
                'review_taste': 3}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # assert that data contains message about not found beer review detail 
        self.assertEqual(response.data, {'detail': ErrorDetail(string='Not found.', code='not_found')})
        self.assertEqual(BeerReview.objects.count(), review_counts)

    def test_update_beer_review_with_invalid_data(self):
        review_counts = BeerReview.objects.count()
        # test username
        test_user_name = 'stcules'
        # we can force authenticate user to bypass explicit token usage when we don't need to test it
        user = User.objects.get(username=test_user_name)
        self.client.force_authenticate(user=user)
        # url for request  
        url = '/beer_review_put'
        data = {'id': 1,
                'review_beer': 'one', 
                'review_overall': 'three.',
                'review_aroma': 'three',
                'review_appearance': 'two',
                'review_palate': 4.5,
                'review_taste': 'string'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # TODO: try to bypass implicit ErrorDetail instansiation
        self.assertEqual(response.data, {
                                            'review_beer': [ErrorDetail('Incorrect type. Expected pk value, received str.', code='incorrect_type')], 
                                            'review_overall': [ErrorDetail('A valid number is required.', code='invalid')],
                                            'review_aroma': [ErrorDetail('A valid integer is required.', code='invalid')], 
                                            'review_appearance': [ErrorDetail('A valid integer is required.', code='invalid')],
                                            'review_palate': [ErrorDetail('A valid integer is required.', code='invalid')], 
                                            'review_taste': [ErrorDetail('A valid integer is required.', code='invalid')]
                                        })
        self.assertEqual(BeerReview.objects.count(), review_counts)

    def test_update_beer_review_with_blank_fields(self):
        review_counts = BeerReview.objects.count()
        # test username
        test_user_name = 'stcules'
        # we can force authenticate user to bypass explicit token usage when we don't need to test it
        user = User.objects.get(username=test_user_name)
        self.client.force_authenticate(user=user)
        # url for request  
        url = '/beer_review_put'
        data = {'id': None,
                'review_beer': None, 
                'review_overall': None,
                'review_aroma': None,
                'review_appearance': None,
                'review_palate': None,
                'review_taste': None}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # assert that data contains message about not found beer review detail 
        self.assertEqual(response.data, {'detail': ErrorDetail(string='Not found.', code='not_found')})
        self.assertEqual(BeerReview.objects.count(), review_counts)

    def test_update_beer_review_without_fields(self):
        review_counts = BeerReview.objects.count()
        # test username
        test_user_name = 'stcules'
        # we can force authenticate user to bypass explicit token usage when we don't need to test it
        user = User.objects.get(username=test_user_name)
        self.client.force_authenticate(user=user)
        # url for request  
        url = '/beer_review_put'
        data = {'id': 1, 'fake_string': 'fake_string'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # TODO: try to bypass implicit ErrorDetail instansiation
        self.assertEqual(response.data, {
                                            'review_beer': [ErrorDetail('This field is required.', code='required')], 
                                            'review_overall': [ErrorDetail('This field is required.', code='required')],
                                            'review_aroma': [ErrorDetail('This field is required.', code='required')], 
                                            'review_appearance': [ErrorDetail('This field is required.', code='required')],
                                            'review_palate': [ErrorDetail('This field is required.', code='required')], 
                                            'review_taste': [ErrorDetail('This field is required.', code='required')]
                                        })
        self.assertEqual(BeerReview.objects.count(), review_counts)


class BeerReviewDetailViewTests(APITestCase):
    
    def test_get_beer_review_detail_for_reviewed_beer_with_valid_token(self):
        """
        Ensure we can get beer review detail for reviewed beer with valid token.
        """
        # test username
        test_user_name = 'stcules'
        # we can force authenticate user to bypass explicit token usage when we don't need to test it
        user = User.objects.get(username=test_user_name)
        self.client.force_authenticate(user=user)
        # url for request        
        url = '/beer_review/973423'
        # get request to url 
        response = self.client.get(url, format='json')
        # test assertions below
        # assert status code equal 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # test that beer review detail contains valid information
        self.assertEqual(response.data['id'], 973423)
        self.assertEqual(response.data['review_beer'], 38567)
        self.assertEqual(response.data['review_time'], '2012-01-06T12:21:32Z')
        self.assertEqual(response.data['beer_name'], 'Karlsberg Black Baron')
        self.assertEqual(response.data['beer_style'], 'Schwarzbier')
        self.assertTrue('/media/images.jpg' in response.data['beer_image'])
        self.assertEqual(response.data['review_overall'], Decimal('2.0'))
        self.assertEqual(response.data['review_aroma'], Decimal('2.0'))
        self.assertEqual(response.data['review_appearance'], Decimal('3.0'))
        self.assertEqual(response.data['review_palate'], Decimal('2.0'))
        self.assertEqual(response.data['review_taste'], Decimal('2.0'))

    def test_get_beer_review_detail_with_invalid_token(self):
        # mannually add invalid credentials to all requests from client 
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format('invalid_test'))
        # url for request        
        url = '/beer/973423'
        # get request to url 
        response = self.client.get(url, format='json')
        # assert status code equal 401
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # assert that data contains message about invalid token
        # ErrorDetail is error class that write errors to response data
        self.assertEqual(response.data, {'detail':  ErrorDetail(string='Invalid token.', code='authentication_failed')})

    def test_get_beer_review_detail_without_token_header(self):
        # url for request        
        url = '/beer/973423'
        # get request to url 
        response = self.client.get(url, format='json')
        # assert status code equal 401
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # assert that data contains message about not provided credentials
        self.assertEqual(response.data, {'detail': ErrorDetail(string='Authentication credentials were not provided.', code='not_authenticated')})
    
    def test_get_beer_review_detail_returns_without_beer_review_id(self):
        # test username
        test_user_name = 'stcules'
        # we can force authenticate user to bypass explicit token usage when we don't need to test it
        user = User.objects.get(username=test_user_name)
        self.client.force_authenticate(user=user)
        # url for request  
        url = '/beer_review/'
        # get request to url 
        response = self.client.get(url, format='json')
        # test that status code equals 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_beer_review_detail_with_review_id_of_another_user(self):
        # url for request        
        url = '/beer_review/973421'
        # review author username
        author_user_name = 'Boto'
        # we can force authenticate user to bypass explicit token usage when we don't need to test it 
        user = User.objects.get(username=author_user_name)
        self.client.force_authenticate(user=user)
        # get request to url 
        response = self.client.get(url, format='json')
        # test authorship of this user
        # assert status code equal 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # test username
        test_user_name = 'stcules'
        # we can force authenticate user to bypass explicit token usage when we don't need to test it
        user = User.objects.get(username=test_user_name)
        self.client.force_authenticate(user=user)
        # get request to url 
        response = self.client.get(url, format='json')
        # test assertions below
        # assert status code equal 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # assert that data contains message about not found beer review detail 
        self.assertEqual(response.data, {'detail': ErrorDetail(string='Not found.', code='not_found')})


class BeerRecommendationDetailViewTests(APITestCase):
    
    def test_get_beer_recommendation_detail_with_valid_token(self):
        """
        Ensure we can get beer recommendation detail with valid token.
        """
        # test username
        test_user_name = 'stcules'
        # we can force authenticate user to bypass explicit token usage when we don't need to test it
        user = User.objects.get(username=test_user_name)
        self.client.force_authenticate(user=user)
        # url for request        
        url = '/beer_recs'
        # get request to url 
        response = self.client.get(url, format='json')
        # test assertions below
        # assert status code equal 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # test that beer recommendation detail contains valid information
        results_dict = response.data['results'][0]
        self.assertEqual(results_dict['id'], 1)
        self.assertEqual(results_dict['top1_beer'], 59054)
        self.assertEqual(results_dict['top2_beer'], 60682)
        self.assertEqual(results_dict['top3_beer'], 50318)
        self.assertEqual(results_dict['top4_beer'], 37600)
        self.assertEqual(results_dict['top5_beer'], 54313)
        self.assertEqual(results_dict['top6_beer'], 3641)
        self.assertEqual(results_dict['top7_beer'], 36603)
        self.assertEqual(results_dict['top8_beer'], 14222)
        self.assertEqual(results_dict['top9_beer'], 32401)
        self.assertEqual(results_dict['top10_beer'], 21497)

    def test_get_beer_recommendation_detail_with_invalid_token(self):
        # mannually add invalid credentials to all requests from client 
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format('invalid_test'))
        # url for request        
        url = '/beer_recs'
        # get request to url 
        response = self.client.get(url, format='json')
        # assert status code equal 401
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # assert that data contains message about invalid token
        # ErrorDetail is error class that write errors to response data
        self.assertEqual(response.data, {'detail':  ErrorDetail(string='Invalid token.', code='authentication_failed')})

    def test_get_beer_recommendation_detail_without_token_header(self):
        # url for request        
        url = '/beer_recs'
        # get request to url 
        response = self.client.get(url, format='json')
        # assert status code equal 401
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # assert that data contains message about not provided credentials
        self.assertEqual(response.data, {'detail': ErrorDetail(string='Authentication credentials were not provided.', code='not_authenticated')})

    def test_get_beer_recommendation_detail_for_new_user(self):
        url = '/registration'
        # data for request
        data = {'email': 'test@user.com', 'password': 'test_password'}
        # post request to url with data in json format 
        response = self.client.post(url, data, format='json')
        # test username
        test_user_name = 'test@user.com'
        # we can force authenticate user to bypass explicit token usage when we don't need to test it
        user = User.objects.get(username=test_user_name)
        self.client.force_authenticate(user=user)
        # url for request  
        url = '/beer_recs'
        # get request to url 
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
