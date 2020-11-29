from rest_framework import generics
from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication
from beer.models import Beer, BeerReview, BeerRecommendation
from django.contrib.auth.models import User
from django.db.models import Avg

class BeerList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Beer.objects.all()
    serializer_class = None

    def get_queryset(self):
        queryset = Beer.objects.all()
        beer_name = self.request.query_params.get('beer_name', None)
        beer_style = self.request.query_params.get('beer_style', None)
        # only_count = self.request.query_params.get('only_count', None)
        if beer_name is not None:
            queryset = queryset.filter(beer_name__icontains=beer_name)
        if beer_style is not None:
            queryset = queryset.filter(beer_style__icontains=beer_style)
        # if only_count is not None:
        #   queryset = Beer.objects.all().count()
        return queryset

class BeerDetail(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Beer.objects.all()
    serializer_class = None

class BeerRatingList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Beer.objects.all().annotate(average_rate=Avg('beerreview__review_overall')).order_by('-average_rate')
    serializer_class = None

class BeerPost(generics.CreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Beer.objects.all()
    serializer_class = None

class BeerReviewList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = BeerReview.objects.all()
    serializer_class = None

    def get_queryset(self, *args, **kwargs):
        return BeerReview.objects.all().filter(review_user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(review_user=self.request.user)

class BeerReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    queryset = BeerReview.objects.all()
    serializer_class = None

    def get_queryset(self, *args, **kwargs):
        return BeerReview.objects.all().filter(review_user=self.request.user)

class BeerRecommendationPost(generics.CreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = BeerRecommendation.objects.all()
    serializer_class = None

    def perform_create(self, serializer):
        serializer.save(recommendation_user=self.request.user)

class BeerRecommendationDetail(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = BeerRecommendation.objects.all()
    serializer_class = None

    def get_queryset(self, *args, **kwargs):
        return BeerRecommendation.objects.all().filter(recommendation_user=self.request.user)

class UserRegistration(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()
    serializer_class = None
