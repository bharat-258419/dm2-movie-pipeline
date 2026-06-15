import requests
import pandas as pd
from google.cloud import bigquery, storage
import json
from datetime import datetime

API_KEY = "f458a4a35d4fb75236e8323374a8a6aa"
PROJECT_ID = "dm2-movie-pipeline"
DATASET_ID = "movies_data"
BUCKET_NAME = "dm2-movie-pipeline-raw"
TABLE_ID = "tmdb_historical"

def fetch_historical_movies():
    all_movies = []
    for year in range(2015, 2025):
        for page in range(1, 6):
            url = f"https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}&language=en-US&sort_by=popularity.desc&primary_release_year={year}&page={page}"
            r = requests.get(url)
            data = r.json()
            movies = data.get("results", [])
            for m in movies:
                m["release_year"] = year
            all_movies.extend(movies)
    return all_movies

def clean_data(movies):
    df = pd.DataFrame(movies)
    df = df[["id","title","release_date","release_year","popularity","vote_average","vote_count","genre_ids","overview","original_language"]]
    df = df.dropna(subset=["title","release_date"])
    df = df[df["vote_count"] > 10]
    df = df[df["vote_average"] > 0]
    df = df.drop_duplicates(subset=["id"])
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
    df["genre_ids"] = df["genre_ids"].apply(lambda x: json.dumps(x))
    df["ingested_at"] = datetime.utcnow().isoformat()
    return df

def upload_to_gcs(df):
    filename = f"historical_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(f"historical/{filename}")
    blob.upload_from_string(df.to_json(orient="records"), content_type="application/json")
    print(f"Uploaded to GCS: historical/{filename}")

def load_to_bigquery(df):
    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()
    print(f"Loaded {len(df)} rows to BigQuery: {table_ref}")

if __name__ == "__main__":
    print("Fetching historical movies (2015-2024)...")
    movies = fetch_historical_movies()
    print(f"Fetched {len(movies)} movies")
    df = clean_data(movies)
    print(f"After cleaning: {len(df)} rows")
    upload_to_gcs(df)
    load_to_bigquery(df)
    print("Done!")
