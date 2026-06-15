SELECT
    id,
    title,
    release_date,
    popularity,
    vote_average,
    vote_count,
    popularity_category,
    ingested_at
FROM {{ source('movies_data', 'tmdb_trending_clean') }}
ORDER BY popularity DESC
LIMIT 20
