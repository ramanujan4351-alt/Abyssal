import os
import re
import json
import subprocess
import psutil
from modules.logs import log_info, log_warn

def load_signatures():
    try:
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sig_path = os.path.join(script_dir, "signatures.json")
        with open(sig_path, "r") as f:
            return json.load(f)
    except Exception as e:
        log_warn(f"[SCAN] Could not load signatures: {e}")
        return {}

def check_firewall_rules():
    """Check and analyze firewall rules for suspicious activity"""
    log_info("[FIREWALL] Checking firewall rules...")
    suspicious_rules = []
    
    try:
        # Check iptables rules
        result = subprocess.run(['sudo', 'iptables', '-L', '-n'], capture_output=True, text=True)
        if result.returncode == 0:
            rules = result.stdout.split('\n')
            for rule in rules:
                if any(keyword in rule.lower() for keyword in ['accept', 'drop', 'reject']):
                    if '0.0.0.0/0' in rule and 'anywhere' in rule:
                        suspicious_rules.append(f"[FIREWALL] Permissive rule: {rule.strip()}")
    except Exception as e:
        log_warn(f"[FIREWALL] Could not check iptables: {e}")
    
    try:
        # Check ufw status
        result = subprocess.run(['sudo', 'ufw', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            if 'Status: inactive' in result.stdout:
                suspicious_rules.append("[FIREWALL] UFW firewall is inactive")
    except Exception as e:
        log_warn(f"[FIREWALL] Could not check UFW: {e}")
    
    return suspicious_rules

def check_network_connections():
    """Check for suspicious network connections"""
    log_info("[FIREWALL] Checking network connections...")
    suspicious_connections = []
    
    try:
        connections = psutil.net_connections()
        for conn in connections:
            if conn.status == 'ESTABLISHED':
                if conn.raddr:
                    ip, port = conn.raddr
                    # Check for connections to suspicious ports
                    if port in [4444, 5555, 6666, 7777, 8888, 9999, 31337, 12345]:
                        suspicious_connections.append(f"[NETWORK] Suspicious port connection: {ip}:{port}")
                    # Check for connections to non-standard ports
                    elif port > 1024 and port not in [8080, 8443, 3000, 5000, 8000, 9000]:
                        suspicious_connections.append(f"[NETWORK] Unusual port connection: {ip}:{port}")
    except Exception as e:
        log_warn(f"[NETWORK] Could not check connections: {e}")
    
    return suspicious_connections

def block_suspicious_ips():
    """Block known malicious IPs using iptables"""
    log_info("[FIREWALL] Setting up IP blocking...")
    
    # Known malicious IP ranges (example - in real implementation, use threat intelligence feeds)
    malicious_ips = [
        "192.168.1.100",  # Example suspicious internal IP
        "10.0.0.50",      # Example suspicious internal IP
    ]
    
    for ip in malicious_ips:
        try:
            subprocess.run(['sudo', 'iptables', '-A', 'INPUT', '-s', ip, '-j', 'DROP'], check=True)
            log_info(f"[FIREWALL] Blocked malicious IP: {ip}")
        except Exception as e:
            log_warn(f"[FIREWALL] Failed to block {ip}: {e}")

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
            # Check for network-related suspicious code
            if any(keyword in content.lower() for keyword in ['socket', 'requests', 'urllib', 'http']):
                if 'connect(' in content or 'get(' in content or 'post(' in content:
                    results.append(f"[ANOMALY] Network activity in {filepath}")
    except Exception as e:
        pass
    return results

def scan_mode():
    log_info("[SCAN] Starting advanced antivirus scan with firewall protection...")
    signatures = load_signatures()
    findings = []
    
    # File system scan
    log_info("[SCAN] Scanning file system...")
    for root, dirs, files in os.walk("/home"):
        for file in files:
            path = os.path.join(root, file)
            if is_hidden(path) and os.access(path, os.X_OK):
                findings.append(f"[ANOMALY] Hidden executable: {path}")
            findings.extend(scan_file(path, signatures))
    
    # Firewall analysis
    firewall_findings = check_firewall_rules()
    findings.extend(firewall_findings)
    
    # Network connection analysis
    network_findings = check_network_connections()
    findings.extend(network_findings)
    
    # Block suspicious IPs
    block_suspicious_ips()
    
    # Report findings
    if findings:
        log_info("[SCAN] Threats detected:")
        for f in findings:
            log_info(f)
    else:
        log_info("[SCAN] No threats found. System is secure.")
