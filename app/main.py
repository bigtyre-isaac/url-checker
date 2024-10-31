# app.py
from flask import Flask, render_template, jsonify
import json
import os
import logging
from filelock import FileLock

app = Flask(__name__)
data_path = "./data/status.json"
lock_path = "./data/status.json.lock"  # Lock file path

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO), format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_status():
    with FileLock(lock_path):
        try:
            with open(data_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not load status data: {e}")
            return {}

@app.route("/")
def index():
    status = load_status()
    return render_template("index.html", status=status)

@app.route("/status")
def status():
    status = load_status()
    return jsonify(status)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
