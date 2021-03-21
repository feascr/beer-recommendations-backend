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
        # we can force authenticate user to bypass explicit token usage when we don't need to test it
        user = User.objects.get(username='stcules')
        self.client.force_authenticate(user=user)
        # url for request  
        url = '/beer'
        # get request to url 
        response = self.client.get(url, format='json')
        # assert data field (contating dict) as you wish

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
        # we can force authenticate user to bypass explicit token usage
        user = User.objects.get(username='stcules')
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
        while (visited_pages - 1) < NUMBER_NEXT_PAGES_TO_CHECK and visited_pages <= num_pages:
            next_url = response.data['next']
            if next_url is not None:
                response = self.client.get(next_url, format='json')
                visited_pages += 1
                self.assertTrue(response.data['previous'] is not None)
            else:
                break

        # calculate number of pages
        num_pages = math.ceil(Beer.objects.count() / settings.REST_FRAMEWORK['PAGE_SIZE'])
        
        url = '/beer?page={}'.format(num_pages)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # assert that response data isn't refer to next page (is None) 
        self.assertTrue(response.data['next'] is None)

    def test_get_beer_list_with_filters(self):
        # calculate number of pages
        num_beers = Beer.objects.all().filter(beer_name__icontains='Light').filter(beer_style__icontains='Lager').count()
        # we can force authenticate user to bypass explicit token usage
        user = User.objects.get(username='stcules')
        self.client.force_authenticate(user=user)
        # url for request  
        url = '/beer?beer_style=Lager&beer_name=Light'
        # get request to url with following all redirections 
        response = self.client.get(url, format='json')
        # assert that response data count is equal to true count after filtering 
        self.assertEqual(response.data['count'], 480)


class BeerDetailViewTests(APITestCase):
    
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
        url = '/beer/100'
        # get request to url 
        response = self.client.get(url, format='json')
        # test assertions below
        # assert status code equal 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_beer_list_with_invalid_token(self):
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

    def test_get_beer_list_without_token_header(self):
        # url for request        
        url = '/beer/100'
        # get request to url 
        response = self.client.get(url, format='json')
        # assert status code equal 401
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # assert that data contains message about not provided credentials
        self.assertEqual(response.data, {'detail': ErrorDetail(string='Authentication credentials were not provided.', code='not_authenticated')})
    
    def test_get_beer_list_returns_without_beer_id(self):
        # we can force authenticate user to bypass explicit token usage when we don't need to test it
        user = User.objects.get(username='stcules')
        self.client.force_authenticate(user=user)
        # url for request  
        url = '/beer/'
        # get request to url 
        response = self.client.get(url, format='json')
        # test that status code equals 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_beer_list_returns_valid_data_without_review_id(self):
        # we can force authenticate user to bypass explicit token usage when we don't need to test it
        user = User.objects.get(username='stcules')
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

    def test_get_beer_list_returns_valid_data_with_review_id(self):
        # we can force authenticate user to bypass explicit token usage when we don't need to test it
        user = User.objects.get(username='stcules')
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
        # we can force authenticate user to bypass explicit token usage
        user = User.objects.get(username='stcules')
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
        while (visited_pages - 1) < NUMBER_NEXT_PAGES_TO_CHECK and visited_pages <= num_pages:
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

        # we can force authenticate user to bypass explicit token usage when we don't need to test it
        user = User.objects.get(username='test@user.com')
        self.client.force_authenticate(user=user)
        # url for request  
        url = '/beer_review'
        # get request to url 
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['results']), 0)

    def test_get_beer_review_list_with_many_reviews_user(self):
        # we can force authenticate user to bypass explicit token usage when we don't need to test it
        user = User.objects.get(username='stcules')
        self.client.force_authenticate(user=user)
        # url for request  
        url = '/beer_review'
        # get request to url 
        response = self.client.get(url, format='json')
        # assert data field (contating dict) as you wish

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

    def test_get_beer_list_returns_valid_redirection_chains(self):
        user = User.objects.get(username='stcules')
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
        while (visited_pages - 1) < NUMBER_NEXT_PAGES_TO_CHECK and visited_pages <= num_pages:
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