import os
from flask import Flask
import redis

app = Flask(__name__)
SITE = os.environ.get("SITE_NAME", "My Site")
CACHE_HOST = os.environ.get("CACHE_HOST", "cache")

store = redis.Redis(host=CACHE_HOST, port=6379)
@app.route("/")
def home():
    hits = store.incr("hits")
    return f"<h1>{SITE}</h1><p>Visits: {hits}</p>"
@app.route("/health")

def health():
    store.ping()
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)