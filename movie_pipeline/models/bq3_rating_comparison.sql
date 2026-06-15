SELECT 'Trending Germany' AS source_type,
    ROUND(AVG(vote_average), 2) AS avg_rating,
    ROUND(AVG(vote_count), 0) AS avg_votes,
    COUNT(*) AS total_movies
FROM {{ source('movies_data', 'tmdb_trending_clean') }}
UNION ALL
SELECT 'Historical 2015-2024' AS source_type,
    ROUND(AVG(vote_average), 2) AS avg_rating,
    ROUND(AVG(vote_count), 0) AS avg_votes,
    COUNT(*) AS total_movies
FROM {{ source('movies_data', 'tmdb_historical_clean') }}
