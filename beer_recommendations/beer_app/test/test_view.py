from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.exceptions import ErrorDetail
from rest_framework.authtoken.models import Token
from beer_app.models import Beer, BeerReview, BeerRecommendation
from django.contrib.auth.models import User
from django.conf import settings
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

        """
        TODO:
            -- test filtering in beer views (views.py L22-L25)
                url example for both:
                /beer?beer_name=Sausa Weizen&beer_style=Hefeweizen
                or for one filter:
                /beer?beer_name=Sausa Weizen
        """

    """
    TODO:
        -- test other views  
    """