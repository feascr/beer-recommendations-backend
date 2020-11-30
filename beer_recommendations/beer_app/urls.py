from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken import views as auth_views
from beer import views as beer_views

urlpatterns = [
    path('beer', beer_views.BeerList.as_view()),
    path('beer_post', beer_views.BeerPost.as_view()),
    path('beer/<int:pk>', beer_views.BeerDetail.as_view()),
    path('beer_rates', beer_views.BeerRatingList.as_view()),
    path('beer_review', beer_views.BeerReviewList.as_view()),
    path('beer_review/<int:pk>', beer_views.BeerReviewDetail.as_view()),
    path('beer_recs', beer_views.BeerRecommendationDetail.as_view()),
    path('registration', beer_views.UserRegistration.as_view()),
    path('api-token-auth', auth_views.obtain_auth_token)
]

urlpatterns = format_suffix_patterns(urlpatterns)
