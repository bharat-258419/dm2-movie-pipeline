#!/bin/bash
export PATH=$PATH:/home/g100004637/.local/bin
cd /home/g100004637/dm2-pipeline

echo "=== Step 1: Ingest TMDB Trending ==="
python3 ingest_tmdb.py

echo "=== Step 2: Ingest Historical Data ==="
python3 ingest_kaggle.py

echo "=== Step 3: Run dbt transformations ==="
cd /home/g100004637/dm2-pipeline/movie_pipeline
dbt run

echo "=== Pipeline Complete ==="
