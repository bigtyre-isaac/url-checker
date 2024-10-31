# url_checker.py
import os
import requests
import json
import time
from datetime import datetime, timezone
import logging
from filelock import FileLock

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO), format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("url_checker")

data_path = "./data/status.json"
lock_path = "./data/status.json.lock"  # Lock file path
check_interval = int(os.getenv("CHECK_INTERVAL", 10))

def load_urls():
    return [value for key, value in os.environ.items() if key.startswith("URL_")]

urls = load_urls()
logger.info(f"Loaded {len(urls)} URLs.")

def save_status(status):
  with FileLock(lock_path):
    with open(data_path, "w") as f:
      json.dump(status, f)

def check_urls():
  logger.info("Starting URL checker.")
  status = {}
  while True:
    for url in urls:
      checkTime = datetime.now(timezone.utc).isoformat()
      try:
        response = requests.get(url, timeout=5)
        code = response.status_code
        status[url] = {"status": code == 200, "code": code, "last_checked": checkTime}
        logger.debug(f"URL {url} responded with status {code}")
      except requests.RequestException:
        status[url] = {"status": False, "code": None, "last_checked": checkTime}
        logger.debug(f"URL {url} failed to respond.")
    save_status(status)
    logger.info(f"Saved status for {len(urls)} URLs.")
    time.sleep(check_interval)

if __name__ == "__main__":
    check_urls()
