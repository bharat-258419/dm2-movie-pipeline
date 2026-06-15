SELECT title, 'Trending' AS data_source, popularity, vote_average, vote_count, popularity_category, CAST(release_date AS STRING) AS release_date
FROM {{ source('movies_data', 'tmdb_trending_clean') }}
UNION ALL
SELECT title, 'Historical' AS data_source, popularity, vote_average, vote_count, rating_category, CAST(release_date AS STRING) AS release_date
FROM {{ source('movies_data', 'tmdb_historical_clean') }}
ORDER BY popularity DESC
LIMIT 25
