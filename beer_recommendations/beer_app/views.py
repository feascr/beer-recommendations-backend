from rest_framework import generics
from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication
from beer.models import Beer, BeerReview, BeerRecommendation
from django.contrib.auth.models import User
from django.db.models import Avg, F
from beer.serializers import (BeerListSerializer, BeerDetailSerializer,
                              BeerReviewListSerializer, BeerReviewPostSerializer, BeerReviewDetailSerializer,
                              BeerRecommendationSerializer,
                              UserSerializer, BeerRatingSerializer)

class BeerList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BeerListSerializer

    def get_queryset(self):
        queryset = Beer.objects.all().annotate(average_rate=Avg('beerreview__review_overall')).order_by(F('average_rate').desc(nulls_last=True))
        beer_name = self.request.query_params.get('beer_name', None)
        beer_style = self.request.query_params.get('beer_style', None)
        if beer_name is not None:
            queryset = queryset.filter(beer_name__icontains=beer_name)
        if beer_style is not None:
            queryset = queryset.filter(beer_style__icontains=beer_style)
        return queryset

class BeerDetail(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Beer.objects.all().annotate(average_rate=Avg('beerreview__review_overall')).order_by(F('average_rate').desc(nulls_last=True))
    serializer_class = BeerDetailSerializer

class BeerRatingList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Beer.objects.all().annotate(average_rate=Avg('beerreview__review_overall')).order_by(F('average_rate').desc(nulls_last=True))
    serializer_class = BeerRatingSerializer

class BeerReviewList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BeerReviewListSerializer

    def get_queryset(self, *args, **kwargs):
        queryset = BeerReview.objects.all().filter(review_user=self.request.user).order_by(F('review_time').desc(nulls_last=True))
        queryset = queryset.annotate(beer_name=F('review_beer__beer_name'), beer_style=F('review_beer__beer_style'), beer_image=F('review_beer__beer_image'))
        print(queryset[0].beer_image)
        return queryset

class BeerReviewPost(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = BeerReview.objects.all()
    serializer_class = BeerReviewPostSerializer

    def perform_create(self, serializer):
        serializer.save(review_user=self.request.user)

class BeerReviewDetail(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BeerReviewDetailSerializer

    def get_queryset(self, *args, **kwargs):
        queryset = BeerReview.objects.all().filter(review_user=self.request.user).order_by(F('review_time').desc(nulls_last=True))
        queryset = queryset.annotate(beer_name=F('review_beer__beer_name'), beer_style=F('review_beer__beer_style'), beer_image=F('review_beer__beer_image'))
        return queryset

class BeerRecommendationPost(generics.CreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = BeerRecommendationSerializer

    def perform_create(self, serializer):
        serializer.save(recommendation_user=self.request.user)

class BeerRecommendationDetail(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BeerRecommendationSerializer

    def get_queryset(self, *args, **kwargs):
        return BeerRecommendation.objects.all().filter(recommendation_user=self.request.user)

class UserRegistration(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSerializer
