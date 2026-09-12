from flask import Flask 
import redis 
import os 

app=Flask(__name__) 

redis_host= os.getenv("REDIS_HOST", "redis")

redis_client = redis.Redis(
    host= redis_host, 
    port=6379 
)

@app.route("/")
def default():
    count = redis_client.incr("views")
    version = os.getenv("VERSION", "default")
    notice = os.getenv("NOTICE_BOARD_NAME")
    return f"""
    <h1>{notice}</h1>
    <p>{count} views</p>
    <p>{version}</p>"""

@app.route("/health") 
def healthcheck():
        try:
             redis_client.ping() 
             return "OK", 200
        except Exception: 
             return "Redis could not be connected!", 500



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001)

