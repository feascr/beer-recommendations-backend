from django.db import models
from django.contrib.auth.models import User


class Beer(models.Model):
    beer_name = models.CharField(max_length=100)
    beer_style = models.CharField(max_length=100)
    brewery_name = models.CharField(max_length=100)
    beer_abv = models.DecimalField(max_digits=5, decimal_places=2)
    beer_image = models.ImageField(upload_to='beer', default='images.jpg', max_length=254)

class BeerReview(models.Model):
    review_user = models.ForeignKey(User, on_delete=models.CASCADE)
    review_beer = models.ForeignKey(Beer, on_delete=models.CASCADE)
    review_time = models.DateTimeField(auto_now=True)
    review_overall = models.DecimalField(max_digits=2, decimal_places=1)
    review_aroma = models.IntegerField()
    review_appearance = models.IntegerField()
    review_palate = models.IntegerField()
    review_taste = models.IntegerField()

class BeerRecommendation(models.Model):
    recommendation_user = models.ForeignKey(User, on_delete=models.CASCADE)
    top1_beer = models.ForeignKey(Beer, related_name='top1_beer', on_delete=models.CASCADE)
    top2_beer = models.ForeignKey(Beer, related_name='top2_beer', on_delete=models.CASCADE)
    top3_beer = models.ForeignKey(Beer, related_name='top3_beer', on_delete=models.CASCADE)
    top4_beer = models.ForeignKey(Beer, related_name='top4_beer', on_delete=models.CASCADE)
    top5_beer = models.ForeignKey(Beer, related_name='top5_beer', on_delete=models.CASCADE)
    top6_beer = models.ForeignKey(Beer, related_name='top6_beer', on_delete=models.CASCADE)
    top7_beer = models.ForeignKey(Beer, related_name='top7_beer', on_delete=models.CASCADE)
    top8_beer = models.ForeignKey(Beer, related_name='top8_beer', on_delete=models.CASCADE)
    top9_beer = models.ForeignKey(Beer, related_name='top9_beer', on_delete=models.CASCADE)
    top10_beer = models.ForeignKey(Beer, related_name='top10_beer', on_delete=models.CASCADE)
