from datetime import datetime
from config import LOG_FILE

def log_to_file(message):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}    {message}\n")
