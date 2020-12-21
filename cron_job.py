# Default libraries
import psycopg2
import pandas as pd
import sys
import random
# Initiate PySpark
# !pip install pyspark
# !pip install -q findspark
from pyspark.sql import SparkSession
spark = SparkSession.builder.master("local[*]").getOrCreate()
# PySpark libraries
from pyspark.ml.recommendation import ALS
import timeit

PATH_TO_DATA = 'D:/TRKPO/beer-recommendations-backend/data_process/'


def connect(params_dic):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params_dic)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        sys.exit(1)
    print("Connection successful")
    return conn

def postgresql_to_dataframe(conn, select_query, column_names):
    """
    Tranform a SELECT query into a pandas dataframe
    """
    cursor = conn.cursor()
    try:
        cursor.execute(select_query)
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        cursor.close()
        return 1


    # Naturally we get a list of tupples
    tupples = cursor.fetchall()
    cursor.close()

    # We just need to turn it into a pandas dataframe
    df = pd.DataFrame(tupples, columns=column_names)
    return df

def recommend(new_users, reviews):
    # Create Spark DataFrame
    beer_ratings = reviews[['user_id', 'beer_id', 'review_overall']]
    beer_ratings = beer_ratings.rename(columns = {'review_overall': 'rating'})
    beer_ratings = spark.createDataFrame(beer_ratings)

    # Select relevant columns & convert the columns to the proper data types
    beer_tbl = beer_ratings.select(beer_ratings.user_id.cast("integer"),
                                 beer_ratings.beer_id.cast("integer"),
                                 beer_ratings.rating.cast("double"))

    # Create ALS model
    als = ALS(userCol="user_id",
              itemCol="beer_id",
              ratingCol="rating",
              rank=10,
              maxIter=15,
              regParam=0.1,
              coldStartStrategy="drop",
              nonnegative=True,
              implicitPrefs=False)

    # Fit the model
    model = als.fit(beer_ratings)

    # Generate n recommendations for all users
    ALS_recommendations = model.recommendForAllUsers(10)

    # Create temporary table
    ALS_recommendations.registerTempTable("ALS_recs_temp")

    # Clean up output, explode it, extract lateral view as separate columns
    clean_recs = spark.sql("SELECT user_id, beer_ids_and_ratings.beer_id AS beer_id,\
                                beer_ids_and_ratings.rating AS prediction \
                                FROM ALS_recs_temp\
                                LATERAL VIEW explode(recommendations) \
                                exploded_table AS beer_ids_and_ratings")

    # Filter for beers that each user has not consumed before
    recommendations = clean_recs.join(beer_ratings.select('user_id', 'beer_id', 'rating'),
                    ['user_id','beer_id'], "left")\
                    .filter(beer_ratings.rating.isNull()).drop('rating')\
                    .distinct()

    recommendations = recommendations.select('user_id', 'beer_id').toPandas()

    # Fill missing recommendations - NEED TO OPTIMIZE
    users_with_not_full_recommends = recommendations[recommendations.groupby('user_id')['user_id'].transform('size') < 10].user_id.unique()
    users_with_not_full_recommends.sort()
    for i in range(0, users_with_not_full_recommends.shape[0]):
        user = users_with_not_full_recommends[i]
        values_to_fill = 10 - recommendations[recommendations.user_id == user].user_id.count()
        beers_not_to_include = reviews[reviews.user_id == user].beer_id.unique()
        not_consumed_beer = list(reviews[~reviews.beer_id.isin(beers_not_to_include)].beer_id.unique())
        for j in range(0, values_to_fill):
            beer_to_insert = random.choice(not_consumed_beer)
            not_consumed_beer.remove(beer_to_insert)
            recommendations = pd.concat([recommendations, pd.DataFrame([[user, beer_to_insert]], columns=recommendations.columns)], ignore_index=True)

    # Sort and reshape
    recommendations = recommendations.sort_values('user_id')
    recommendations['beer_id_field_name'] = ['Rec'+ str(i) for i in range(0, 10)] * (recommendations.shape[0] // 10)
    recommendations = recommendations.pivot(index='user_id', columns='beer_id_field_name', values='beer_id')
    recommendations.columns = recommendations.columns.ravel()
    recommendations.reset_index(inplace=True)

    # Add users with no reviews - fill recommendations using top 10 beers with > 1000 reviews
    top_10_rec = reviews[['beer_id', 'review_overall']]\
        .pivot_table(index="beer_id", aggfunc=("count",'mean'))\
        .dropna()

    # Rename columns and flatten pivot table
    top_10_rec.columns = top_10_rec.columns.to_series().str.join('_')
    top_10_rec.reset_index(inplace=True)

    # Filter for highest rated beers
    top_10_rec = top_10_rec.query('review_overall_count >= 1000')\
    .sort_values('review_overall_mean', ascending=False)\
    .head(10)

    top_10 = top_10_rec.beer_id.values

    # Add to resulting df
    for new_user in new_users:
        new_row = list(top_10)
        new_row.insert(0, new_user)
        recommendations = pd.concat([recommendations, pd.DataFrame([new_row], columns=recommendations.columns)], ignore_index=True)

    return recommendations, users_with_not_full_recommends


start = timeit.default_timer()
params_dic = {
    'host'      : 'localhost',
    'database'  : 'beer_recommendations',
    'user'      : 'beer_lover',
    'password'  : 'lovebeer'
}

# Connect to the database
conn = connect(params_dic)
column_names = ['user_id', 'beer_id', 'review_overall']
# Execute the "SELECT *" query
review_df = postgresql_to_dataframe(conn, 'SELECT review_user_id, review_beer_id, review_overall FROM beer_beerreview', column_names)
column_names = ['user_id']
new_users = postgresql_to_dataframe(conn, 'SELECT id FROM auth_user WHERE  id NOT IN (SELECT DISTINCT review_user_id FROM beer_beerreview)', column_names)
print('DFs are built')

reviews = review_df.copy()
new_users = new_users.copy()
# Review scores of >= 1
reviews = reviews[(reviews['review_overall'] >= 1)]
recommendations, users_with_not_full_recommends = recommend(new_users, reviews)
print('Recs are built')

recommendations.to_csv(PATH_TO_DATA + 'recommendations.csv', index=False)
with open(PATH_TO_DATA + 'users_with_not_full_recommends.txt', 'w') as f:
    for item in users_with_not_full_recommends:
        f.write("%d\n" % item)

cursor = conn.cursor()
cursor.execute('BEGIN;')
try:
    cursor.execute('TRUNCATE beer_beerrecommendation;')
except (Exception, psycopg2.DatabaseError) as error:
    print("Error: %s" % error)
    cursor.execute('ROLBACK;')
    cursor.close()
    sys.exit(1)
print('Table is truncated')

try:
    request = "COPY beer_beerrecommendation (recommendation_user_id, top1_beer_id, top2_beer_id, top3_beer_id, top4_beer_id, top5_beer_id, top6_beer_id, top7_beer_id, top8_beer_id, top9_beer_id, top10_beer_id) FROM '{}' DELIMITER ',' CSV HEADER ENCODING 'UTF8';".format(PATH_TO_DATA + 'recommendations.csv')
    cursor.execute(request)
except (Exception, psycopg2.DatabaseError) as error:
    print("Error: %s" % error)
    cursor.execute('ROLBACK;')
    cursor.close()
    sys.exit(1)
print('Copy to db')
cursor.execute('COMMIT;')
stop = timeit.default_timer()
print('Work time is', stop - start)
conn.close()
