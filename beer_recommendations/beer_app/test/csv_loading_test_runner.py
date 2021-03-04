import os
from django.test.runner import DiscoverRunner
from django.conf import settings


class CSVLoadingTestRunner(DiscoverRunner):

    def setup_databases(self, *args, **kwargs):
        old_names = super(CSVLoadingTestRunner, self).setup_databases(*args, **kwargs)
        from django.db import connection
        with connection.cursor() as cursor:
            test_data_path = os.path.join(settings.BASE_DIR, 'beer_app', 'test', 'test_data')
            user_csv_path = os.path.join(test_data_path, 'user.csv')
            beer_csv_path = os.path.join(test_data_path, 'beer.csv')
            beer_review_csv_path = os.path.join(test_data_path, 'review.csv')
            beer_recommendations_csv_path = os.path.join(test_data_path, 'recommendations.csv')
            cursor.execute("""
                           COPY auth_user(username, email, password, is_superuser, is_staff, is_active, first_name, last_name, date_joined)
                           FROM %s
                           DELIMITER ','
                           CSV HEADER;
                           """, [user_csv_path])
            cursor.execute("""
                           COPY beer_app_beer(beer_name, beer_style, brewery_name, beer_abv, beer_image)
                           FROM %s
                           DELIMITER ','
                           CSV HEADER;
                           """, [beer_csv_path])
            cursor.execute("""
                           COPY beer_app_beerreview(review_time, review_overall, review_aroma, review_appearance, review_palate, review_taste, review_user_id, review_beer_id)
                           FROM %s
                           DELIMITER ','
                           CSV HEADER;
                           """, [beer_review_csv_path])
            cursor.execute("""
                           COPY beer_app_beerrecommendation(recommendation_user_id, top1_beer_id, top2_beer_id, top3_beer_id, top4_beer_id, top5_beer_id, top6_beer_id, top7_beer_id, top8_beer_id, top9_beer_id, top10_beer_id)
                           FROM %s
                           DELIMITER ';'
                           CSV HEADER;
                           """, [beer_recommendations_csv_path])
        return old_names

    def teardown_databases(self, *args, **kwargs):
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                           DELETE FROM beer_app_beerrecommendation;
                           """)
            cursor.execute("""
                           DELETE FROM beer_app_beerreview;
                           """)
            cursor.execute("""
                           DELETE FROM beer_app_beer;
                           """)
            cursor.execute("""
                           DELETE FROM auth_user;
                           """)
        super(CSVLoadingTestRunner, self).teardown_databases(*args, **kwargs)
