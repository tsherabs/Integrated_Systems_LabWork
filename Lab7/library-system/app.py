from flask import Flask 
import os 
import redis 

app = Flask(__name__)

library_name = os.getenv("LIBRARY_NAME", "Default Library")

redis_client = redis.Redis(
    host = "redis", 
    port = 6379, 
    decode_responses = True 
)

@app.route("/")
def borrow(): 
    count = redis_client.incr("borrow_count")


    return f"""<h1>Welcome to {library_name}</h1>
    <p>The borrow counts are {count}</p>"""

@app.route("/health")
def healthcheck():
    try: 
        redis_client.ping()
        return "OK", 200 
    except: 
        return "Redis is not available", 500

if __name__ == "__main__": 
    app.run(host = "0.0.0.0", port = 5000)

