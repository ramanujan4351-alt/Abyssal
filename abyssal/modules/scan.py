import os
import re
import json
from modules.logs import log_info, log_warn

def load_signatures():
    try:
        with open("signatures.json", "r") as f:
            return json.load(f)
    except Exception as e:
        log_warn(f"[SCAN] Could not load signatures: {e}")
        return {}

def is_hidden(filepath):
    return any(part.startswith('.') for part in filepath.split(os.sep))

def scan_file(filepath, signatures):
    results = []
    try:
        with open(filepath, 'r', errors='ignore') as f:
            content = f.read()
            for name, pattern in signatures.items():
                if re.search(pattern, content, re.IGNORECASE):
                    results.append(f"[MATCH] {name} in {filepath}")
            # Anomaly: suspicious script
            if filepath.endswith(('.sh', '.py', '.pl', '.js')) and 'eval(' in content:
                results.append(f"[ANOMALY] Obfuscated code in {filepath}")
    except Exception as e:
        pass
    return results

def scan_mode():
    log_info("[SCAN] Starting custom antivirus scan...")
    signatures = load_signatures()
    findings = []
    for root, dirs, files in os.walk("/home"):
        for file in files:
            path = os.path.join(root, file)
            if is_hidden(path) and os.access(path, os.X_OK):
                findings.append(f"[ANOMALY] Hidden executable: {path}")
            findings.extend(scan_file(path, signatures))
    if findings:
        for f in findings:
            log_info(f)
    else:
        log_info("[SCAN] No threats found.")
