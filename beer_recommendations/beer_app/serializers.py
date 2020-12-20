from rest_framework import serializers
from beer.models import Beer, BeerReview, BeerRecommendation
from django.conf import settings
from django.contrib.auth.models import User


class BeerListSerializer(serializers.ModelSerializer):
    average_rate = serializers.DecimalField(max_digits=2, decimal_places=1)
    class Meta:
    	model = Beer
    	fields = ['id',
    	          'beer_name',
    	          'beer_style',
    	          'average_rate',
                  'beer_image']

class BeerDetailSerializer(serializers.ModelSerializer):
    average_rate = serializers.DecimalField(max_digits=2, decimal_places=1)
    average_aroma = serializers.DecimalField(max_digits=2, decimal_places=1)
    average_appearance = serializers.DecimalField(max_digits=2, decimal_places=1)
    average_palate = serializers.DecimalField(max_digits=2, decimal_places=1)
    average_taste = serializers.DecimalField(max_digits=2, decimal_places=1)
    is_reviewed = serializers.DecimalField(max_digits=2, decimal_places=1)
    class Meta:
        model = Beer
        fields = ['id',
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
                  'is_reviewed']

class BeerRatingSerializer(serializers.ModelSerializer):
	average_rate = serializers.DecimalField(max_digits=2, decimal_places=1)
	class Meta:
		model = Beer
		fields = ['id',
				  'beer_name',
				  'beer_style',
				  'brewery_name',
				  'beer_abv',
				  'average_rate',
                  'beer_image']

class BeerReviewListSerializer(serializers.ModelSerializer):
    beer_name = serializers.CharField(max_length=100)
    beer_style = serializers.CharField(max_length=100)
    beer_image = serializers.SerializerMethodField('get_image_url')
    class Meta:
    	model = BeerReview
    	fields = ['id',
    	          'review_beer',
                  'review_time',
                  'beer_name',
                  'beer_style',
                  'beer_image',
    	          'review_overall']

    def get_image_url(self, obj):
        return self.context['request'].build_absolute_uri(settings.MEDIA_URL + obj.beer_image)

class BeerReviewPutPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeerReview
        fields = ['id',
                  'review_beer',
                  'review_time',
                  'review_overall',
                  'review_aroma',
                  'review_appearance',
                  'review_palate',
                  'review_taste']

class BeerReviewDetailSerializer(serializers.ModelSerializer):
    beer_name = serializers.CharField(max_length=100)
    beer_style = serializers.CharField(max_length=100)
    beer_image = serializers.SerializerMethodField('get_image_url')
    class Meta:
        model = BeerReview
        fields = ['id',
                  'review_beer',
                  'review_time',
                  'beer_name',
                  'beer_style',
                  'beer_image',
                  'review_overall',
                  'review_aroma',
                  'review_appearance',
                  'review_palate',
                  'review_taste']

    def get_image_url(self, obj):
        return self.context['request'].build_absolute_uri(settings.MEDIA_URL + obj.beer_image)

class BeerRecommendationSerializer(serializers.ModelSerializer):
	recommendation_user = serializers.ReadOnlyField(source='recommendation_user.username')
	class Meta:
		model = BeerRecommendation
		fields = ['id',
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
    			  'top10_beer']

class UserSerializer(serializers.ModelSerializer):
	password = serializers.CharField(max_length=100, write_only=True)

	def create(self, validated_data):
		user = User(email=validated_data['email'], username=validated_data['email'])
		user.set_password(validated_data['password'])
		user.save()
		return user

	class Meta:
		model = User
		fields = ['email', 'password']

