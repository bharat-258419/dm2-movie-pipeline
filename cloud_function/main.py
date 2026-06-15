import functions_framework
import subprocess
import os

@functions_framework.http
def run_pipeline(request):
    try:
        result = subprocess.run(
            ['python3', '/home/user/ingest_tmdb.py'],
            capture_output=True, text=True, timeout=300
        )
        return f"Pipeline triggered successfully", 200
    except Exception as e:
        return f"Error: {str(e)}", 500
