WITH exploded AS (
    SELECT id, title, popularity, CAST(genre_id AS INT64) AS genre_id
    FROM {{ source('movies_data', 'tmdb_trending_clean') }},
    UNNEST(JSON_VALUE_ARRAY(genre_ids)) AS genre_id
),
genre_map AS (
    SELECT * FROM UNNEST([
        STRUCT(28 AS genre_id, 'Action' AS genre_name),
        STRUCT(12, 'Adventure'), STRUCT(16, 'Animation'),
        STRUCT(35, 'Comedy'), STRUCT(80, 'Crime'),
        STRUCT(99, 'Documentary'), STRUCT(18, 'Drama'),
        STRUCT(10751, 'Family'), STRUCT(14, 'Fantasy'),
        STRUCT(36, 'History'), STRUCT(27, 'Horror'),
        STRUCT(10402, 'Music'), STRUCT(9648, 'Mystery'),
        STRUCT(10749, 'Romance'), STRUCT(878, 'Sci-Fi'),
        STRUCT(53, 'Thriller'), STRUCT(10752, 'War'),
        STRUCT(37, 'Western')
    ])
)
SELECT
    gm.genre_name,
    COUNT(e.id) AS movie_count,
    ROUND(AVG(e.popularity), 2) AS avg_popularity
FROM exploded e
JOIN genre_map gm ON e.genre_id = gm.genre_id
GROUP BY gm.genre_name
ORDER BY movie_count DESC
