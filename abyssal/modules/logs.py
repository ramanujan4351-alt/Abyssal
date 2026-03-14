import datetime

def log_info(msg):
    print(f"[Abyssal][{datetime.datetime.now().isoformat()}] {msg}")

def log_warn(msg):
    print(f"[Abyssal][{datetime.datetime.now().isoformat()}][WARN] {msg}")
