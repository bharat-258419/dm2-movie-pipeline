WITH ranked AS (
    SELECT
        title, release_year, vote_average, vote_count, rating_category,
        ROW_NUMBER() OVER (PARTITION BY release_year ORDER BY vote_average DESC, vote_count DESC) AS rank
    FROM {{ source('movies_data', 'tmdb_historical_clean') }}
    WHERE release_year BETWEEN 2015 AND 2024 AND vote_count >= 50
)
SELECT title, release_year, vote_average, vote_count, rating_category, rank
FROM ranked WHERE rank <= 3
ORDER BY release_year DESC, rank
