import requests
import pandas as pd
from google.cloud import bigquery, storage
import json
from datetime import datetime

# Config
API_KEY = "f458a4a35d4fb75236e8323374a8a6aa"
PROJECT_ID = "dm2-movie-pipeline"
DATASET_ID = "movies_data"
BUCKET_NAME = "dm2-movie-pipeline-raw"
TABLE_ID = "tmdb_trending"

def fetch_tmdb_trending():
    url = f"https://api.themoviedb.org/3/trending/movie/day?api_key={API_KEY}&language=en-US&region=DE"
    all_movies = []
    for page in range(1, 6):
        r = requests.get(url + f"&page={page}")
        data = r.json()
        all_movies.extend(data.get("results", []))
    return all_movies

def clean_data(movies):
    df = pd.DataFrame(movies)
    df = df[["id","title","release_date","popularity","vote_average","vote_count","genre_ids","overview"]]
    df = df.dropna(subset=["title", "release_date"])
    df = df[df["vote_count"] > 0]
    df = df.drop_duplicates(subset=["id"])
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
    df["genre_ids"] = df["genre_ids"].apply(lambda x: json.dumps(x))
    df["ingested_at"] = datetime.utcnow().isoformat()
    return df

def upload_to_gcs(df):
    filename = f"tmdb_trending_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(f"tmdb/{filename}")
    blob.upload_from_string(df.to_json(orient="records"), content_type="application/json")
    print(f"Uploaded to GCS: tmdb/{filename}")
    return f"gs://{BUCKET_NAME}/tmdb/{filename}"

def load_to_bigquery(df):
    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()
    print(f"Loaded {len(df)} rows to BigQuery: {table_ref}")

if __name__ == "__main__":
    print("Fetching TMDB trending movies...")
    movies = fetch_tmdb_trending()
    print(f"Fetched {len(movies)} movies")
    df = clean_data(movies)
    print(f"After cleaning: {len(df)} rows")
    upload_to_gcs(df)
    load_to_bigquery(df)
    print("Done!")
