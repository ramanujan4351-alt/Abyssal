import subprocess
import random
import string
import time
from modules.logs import log_info, log_warn

def random_hostname():
    ts = int(time.time())
    rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"abyssal-{rand}-{ts}"

def anon_mode():
    log_info("[ANON] Starting anonymity mode...")
    try:
        subprocess.run(["sudo", "systemctl", "start", "tor"], check=True)
        log_info("[ANON] Tor service started.")
    except Exception as e:
        log_warn(f"[ANON] Failed to start Tor: {e}")
    try:
        subprocess.run(["sudo", "macchanger", "-r", "eth0"], check=True)
        log_info("[ANON] MAC address randomized on eth0.")
    except Exception as e:
        log_warn(f"[ANON] Failed to randomize MAC: {e}")
    try:
        new_host = random_hostname()
        subprocess.run(["sudo", "hostnamectl", "set-hostname", new_host], check=True)
        log_info(f"[ANON] Hostname changed to {new_host}.")
    except Exception as e:
        log_warn(f"[ANON] Failed to change hostname: {e}")
    try:
        subprocess.run(["sudo", "systemd-resolve", "--flush-caches"], check=True)
        log_info("[ANON] DNS cache flushed.")
    except Exception as e:
        log_warn(f"[ANON] Failed to flush DNS cache: {e}")
