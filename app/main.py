from flask import Flask, render_template, jsonify
import json
import os
import logging
from filelock import FileLock
from prometheus_client import make_wsgi_app, Gauge, CollectorRegistry
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__)
registry = CollectorRegistry(auto_describe=False)
url_up = Gauge('url_response_success', 'URL Up/Down Status', ['url'], registry=registry)

data_path = "./data/status.json"
lock_path = "./data/status.json.lock"

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO), format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("Application started.")
base_path = os.getenv("BASE_PATH", "/")
logger.info(f"Using base path: {base_path}")

def load_status():
  with FileLock(lock_path):
    try:
      with open(data_path, "r") as f:
        data = json.load(f)
        for url, info in data.items():
            url_up.labels(url).set(1 if info['status'] else 0)
        return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
      logger.warning(f"Could not load status data: {e}")
      return {}

@app.route("/")
def index():
    status = load_status()
    return render_template("index.html", status=status, base_path=base_path)

@app.route("/status")
def status():
    status = load_status()
    return jsonify(status)

# Add route for Prometheus metrics
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app(registry)
})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
