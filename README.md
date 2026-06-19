# DM2 Movie Pipeline

GCP data pipeline project for **Data Management 2 (DM2)** at SRH Heidelberg — ingests live movie data from TMDB, cleans it with Spark, transforms it with dbt, and serves it through BigQuery + Looker Studio. The enriched dataset from this pipeline was later used in the separate [DVS3 "Hype vs Heart vs Money" Tableau project](https://github.com/bharat-258419/dvs3-hype-vs-heart-vs-money-project).


## Architecture

TMDB API → Cloud Storage (raw JSON) → BigQuery (raw tables) → Dataproc/PySpark (cleaning) → dbt (BQ1–BQ5 models) → Looker Studio

A Cloud Scheduler job triggers a Cloud Function daily (midnight, Berlin time) to run ingestion automatically.

## GCP Setup

- Project: `dm2-movie-pipeline`
- Storage bucket: `dm2-movie-pipeline-raw`
- BigQuery dataset: `movies_data` (europe-west3)
- Scheduler job: `daily-movie-pipeline`

## Pipeline Components

- **`ingest_tmdb.py`** — pulls today's trending movies from the TMDB API (5 pages, Germany region), cleans them (dedupe, drop rows missing title/date, vote_count > 0), writes raw JSON to GCS, loads to BigQuery `tmdb_trending`.
- **`ingest_kaggle.py`** — pulls historical movies (2015–2024) from the TMDB discover endpoint, filters for vote_count > 10 and rated movies, loads to BigQuery `tmdb_historical`.
- **`spark_clean.py`** — PySpark/Dataproc job that reads both raw tables from BigQuery, filters and deduplicates them, adds `popularity_category` (High/Medium/Low) and `rating_category` (Excellent/Good/Average) labels, writes cleaned versions back as `tmdb_trending_clean` / `tmdb_historical_clean`.
- **`movie_pipeline/`** — dbt project with 5 models: `bq1_trending_germany`, `bq2_genre_popularity`, `bq3_rating_comparison`, `bq4_top_rated_by_year`, `bq5_popularity_leaders`.
- **`cloud_function/main.py`** — HTTP Cloud Function that triggers ingestion; called daily by Cloud Scheduler.
- **`run_pipeline.sh`** — runs the pipeline end-to-end (ingest trending → ingest historical → dbt run).
- **`logs/`** — pipeline run logs.

## Tech Stack

Google Cloud Platform (BigQuery, Cloud Storage, Dataproc, Cloud Functions, Cloud Scheduler), PySpark, dbt Core, Python (pandas, requests), Looker Studio.
