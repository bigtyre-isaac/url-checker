from flask import Flask, render_template, jsonify
from prometheus_client import Gauge, start_http_server
import os
import requests
import threading
import time
import json
from datetime import datetime

# Load URLs based on the prefix pattern
def load_urls():
    return [value for key, value in os.environ.items() if key.startswith("URL_")]

urls = load_urls()  # Dynamically get URLs at startup

# App configuration
app = Flask(__name__)
data_path = "./data/status.json"
#urls = os.getenv("URLS", "").split(",")
check_interval = int(os.getenv("CHECK_INTERVAL", 10))

# Prometheus Metrics
status_gauge = Gauge("url_status", "Status of the URLs", ["url"])
response_code_gauge = Gauge("url_response_code", "Last response code of the URLs", ["url"])

# Load status data, filtering out entries not in the current URLs
def load_status():
    try:
        with open(data_path, "r") as f:
            status = json.load(f)
    except FileNotFoundError:
        status = {}

    # Filter out any URLs that are not in the current environment-defined list
    filtered_status = {url: status.get(url, {"status": False, "code": None, "last_checked": None}) for url in urls}
    return filtered_status

# Save status only for the currently active URLs
def save_status(status):
    current_status = {url: status[url] for url in urls}
    with open(data_path, "w") as f:
        json.dump(current_status, f)

# Background thread to check URLs
def check_urls():
    status = load_status()
    while True:
        for url in urls:
            checkTime = datetime.now(timezone.utc).isoformat()
            try:
                response = requests.get(url, timeout=5)
                code = response.status_code
                status[url] = {
                    "status": code == 200,
                    "code": code,
                    "last_checked": checkTime
                }
                status_gauge.labels(url=url).set(1 if code == 200 else 0)
                response_code_gauge.labels(url=url).set(code)
            except requests.RequestException:
                status[url] = {
                    "status": False,
                    "code": None,
                    "last_checked": checkTime
                }
                status_gauge.labels(url=url).set(0)
                response_code_gauge.labels(url=url).set(-1)
        
        save_status(status)
        time.sleep(check_interval)

# Serve status on homepage
@app.route("/")
def index():
    status = load_status()
    return render_template("index.html", status=status)

# Serve JSON data for status
@app.route("/status")
def status():
    status = load_status()
    return jsonify(status)

# Run background thread
threading.Thread(target=check_urls, daemon=True).start()

# Function to start Prometheus in a separate thread
def start_prometheus():
    start_http_server(8000)  # Use a different port to avoid conflicts

# Start Prometheus if running directly
if __name__ == "__main__":
    Thread(target=start_prometheus, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)


