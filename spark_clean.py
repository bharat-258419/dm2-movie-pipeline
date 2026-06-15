from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, year, month, regexp_replace, size, from_json
from pyspark.sql.types import ArrayType, IntegerType
import json

PROJECT_ID = "dm2-movie-pipeline"
DATASET = "movies_data"
BUCKET = "dm2-movie-pipeline-raw"

spark = SparkSession.builder \
    .appName("MovieDataCleaning") \
    .config("spark.jars.packages", "com.google.cloud.spark:spark-bigquery-with-dependencies_2.12:0.32.2") \
    .getOrCreate()

spark.conf.set("temporaryGcsBucket", BUCKET)

# Load trending data
trending = spark.read.format("bigquery") \
    .option("table", f"{PROJECT_ID}.{DATASET}.tmdb_trending") \
    .load()

# Load historical data
historical = spark.read.format("bigquery") \
    .option("table", f"{PROJECT_ID}.{DATASET}.tmdb_historical") \
    .load()

# Clean trending
trending_clean = trending \
    .filter(col("vote_count") > 0) \
    .filter(col("popularity") > 0) \
    .withColumn("popularity_category",
        when(col("popularity") > 100, "High")
        .when(col("popularity") > 50, "Medium")
        .otherwise("Low")) \
    .dropDuplicates(["id"])

# Clean historical
historical_clean = historical \
    .filter(col("vote_count") > 10) \
    .filter(col("vote_average") > 0) \
    .withColumn("rating_category",
        when(col("vote_average") >= 7.5, "Excellent")
        .when(col("vote_average") >= 6.0, "Good")
        .otherwise("Average")) \
    .dropDuplicates(["id"])

# Write back to BigQuery
trending_clean.write.format("bigquery") \
    .option("table", f"{PROJECT_ID}.{DATASET}.tmdb_trending_clean") \
    .option("writeDisposition", "WRITE_TRUNCATE") \
    .save()

historical_clean.write.format("bigquery") \
    .option("table", f"{PROJECT_ID}.{DATASET}.tmdb_historical_clean") \
    .option("writeDisposition", "WRITE_TRUNCATE") \
    .save()

print(f"Trending clean rows: {trending_clean.count()}")
print(f"Historical clean rows: {historical_clean.count()}")
spark.stop()
