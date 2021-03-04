from rest_framework import serializers
from beer_app.models import Beer, BeerReview, BeerRecommendation
from django.conf import settings
from django.db.models import Avg, Count, F
from django.contrib.auth.models import User
from random import randint
from rest_framework.validators import UniqueValidator



class BeerListSerializer(serializers.ModelSerializer):
    average_rate = serializers.DecimalField(max_digits=2, decimal_places=1)
    class Meta:
        model = Beer
        fields = [
                    'id',
                    'beer_name',
                    'beer_style',
                    'average_rate',
                    'beer_image'
                 ]

class BeerDetailSerializer(serializers.ModelSerializer):
    average_rate = serializers.DecimalField(max_digits=2, decimal_places=1)
    average_aroma = serializers.DecimalField(max_digits=2, decimal_places=1)
    average_appearance = serializers.DecimalField(max_digits=2, decimal_places=1)
    average_palate = serializers.DecimalField(max_digits=2, decimal_places=1)
    average_taste = serializers.DecimalField(max_digits=2, decimal_places=1)
    is_reviewed = serializers.IntegerField()
    class Meta:
        model = Beer
        fields = [
                    'id',
                    'beer_name',
                    'beer_style',
                    'brewery_name',
                    'beer_abv',
                    'average_rate',
                    'average_aroma',
                    'average_appearance',
                    'average_palate',
                    'average_taste',
                    'beer_image',
                    'is_reviewed'
                 ]

class BeerRatingSerializer(serializers.ModelSerializer):
    average_rate = serializers.DecimalField(max_digits=2, decimal_places=1)
    class Meta:
        model = Beer
        fields = [
                    'id',
                    'beer_name',
                    'beer_style',
                    'brewery_name',
                    'beer_abv',
                    'average_rate',
                    'beer_image'
                 ]

class BeerReviewListSerializer(serializers.ModelSerializer):
    beer_name = serializers.CharField(max_length=100)
    beer_style = serializers.CharField(max_length=100)
    beer_image = serializers.SerializerMethodField('get_image_url')
    class Meta:
        model = BeerReview
        fields = [
                    'id',
                    'review_beer',
                    'review_time',
                    'beer_name',
                    'beer_style',
                    'beer_image',
                    'review_overall'
                 ]

    def get_image_url(self, obj):
        return self.context['request'].build_absolute_uri(settings.MEDIA_URL + obj.beer_image)

class BeerReviewPutPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeerReview
        fields = [
                    'id',
                    'review_beer',
                    'review_time',
                    'review_overall',
                    'review_aroma',
                    'review_appearance',
                    'review_palate',
                    'review_taste'
                 ]

class BeerReviewDetailSerializer(serializers.ModelSerializer):
    beer_name = serializers.CharField(max_length=100)
    beer_style = serializers.CharField(max_length=100)
    beer_image = serializers.SerializerMethodField('get_image_url')
    class Meta:
        model = BeerReview
        fields = [
                    'id',
                    'review_beer',
                    'review_time',
                    'beer_name',
                    'beer_style',
                    'beer_image',
                    'review_overall',
                    'review_aroma',
                    'review_appearance',
                    'review_palate',
                    'review_taste'
                 ]

    def get_image_url(self, obj):
        return self.context['request'].build_absolute_uri(settings.MEDIA_URL + obj.beer_image)

class BeerRecommendationSerializer(serializers.ModelSerializer):
    recommendation_user = serializers.ReadOnlyField(source='recommendation_user.username')
    class Meta:
        model = BeerRecommendation
        fields = [
                    'id',
                    'recommendation_user',
                    'top1_beer',
                    'top2_beer',
                    'top3_beer',
                    'top4_beer',
                    'top5_beer',
                    'top6_beer',
                    'top7_beer',
                    'top8_beer',
                    'top9_beer',
                    'top10_beer'
                 ]

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=100, write_only=True)
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ['email', 'password']

    def create(self, validated_data):
        user = User(email=validated_data['email'], username=validated_data['email'])
        user.set_password(validated_data['password'])
        # queryset = Beer.objects.all().annotate(count=Count('beerreview__review_overall')).filter(count__gt=1000).annotate(average_rate=Avg('beerreview__review_overall')).order_by(F('average_rate').desc(nulls_last=True))[:10]
        queryset = BeerReview.objects.all().values('review_beer').annotate(count=Count('review_overall')).filter(count__gt=1000).values('review_beer').annotate(average_rate=Avg('review_overall')).order_by(F('average_rate').desc(nulls_last=True)).values_list('review_beer')[:10]
        # queryset = Beer.objects.all()
        # count = queryset.aggregate(count=Count('id'))['count']
        # top_beers = []
        # for i in range(10):
        #   random_index = randint(0, count - 1)
        #   top_beers.append(queryset[random_index])
        recommendations = BeerRecommendation(recommendation_user=user, top1_beer=Beer.objects.get(id=queryset[0][0]),
                                                                       top2_beer=Beer.objects.get(id=queryset[1][0]),
                                                                       top3_beer=Beer.objects.get(id=queryset[2][0]),
                                                                       top4_beer=Beer.objects.get(id=queryset[3][0]),
                                                                       top5_beer=Beer.objects.get(id=queryset[4][0]),
                                                                       top6_beer=Beer.objects.get(id=queryset[5][0]),
                                                                       top7_beer=Beer.objects.get(id=queryset[6][0]),
                                                                       top8_beer=Beer.objects.get(id=queryset[7][0]),
                                                                       top9_beer=Beer.objects.get(id=queryset[8][0]),
                                                                       top10_beer=Beer.objects.get(id=[9][0]))
        user.save()
        recommendations.save()
        return user
