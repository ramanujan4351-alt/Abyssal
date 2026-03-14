import subprocess
from modules.logs import log_info, log_warn

def harden_mode():
    log_info("[HARDEN] Running Lynis system audit...")
    try:
        result = subprocess.run(["sudo", "lynis", "audit", "system"], capture_output=True, text=True)
        output = result.stdout
        summary = []
        capture = False
        for line in output.splitlines():
            if "Hardening index" in line or "Suggestions" in line or "Warnings" in line:
                capture = True
            if capture:
                summary.append(line)
        log_info("[HARDEN] Lynis summary:")
        for line in summary:
            log_info(line)
    except Exception as e:
        log_warn(f"[HARDEN] Lynis failed: {e}")
