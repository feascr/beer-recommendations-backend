from rest_framework import serializers
from beer.models import Beer, BeerReview, BeerRecommendation
from django.contrib.auth.models import User


class BeerSerializer(serializers.ModelSerializer):
    class Meta:
    	model = Beer
    	fields = ['id', 
    	          'beer_name', 
    	          'beer_style', 
    	          'brewery_name', 
    	          'beer_abv']

class BeerRatingSerializer(serializers.ModelSerializer):
	average_rate = serializers.DecimalField(max_digits=2, decimal_places=1)
	class Meta:
		model = Beer
		fields = ['id', 
				  'beer_name', 
				  'beer_style', 
				  'brewery_name', 
				  'beer_abv',
				  'average_rate']

	# def get_beer_rating(self, obj):
	# 	beer_rating = BeerReview.objects.all().filter(review_beer=obj.pk).aggregate(Avg('review_overall')).get('review_overall__avg')
	# 	return beer_rating


class BeerReviewSerializer(serializers.ModelSerializer):
    review_user = serializers.ReadOnlyField(source='review_user.username')
    class Meta:
    	model = BeerReview
    	fields = ['id',
    	          'review_user',
    	          'review_beer',
    	          'review_time',
    	          'review_overall',
    	          'review_aroma',
    	          'review_appearance',
    	          'review_palate',
    	          'review_taste']

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

