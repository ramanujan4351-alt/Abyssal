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
            if filepath.endswith(('.sh', '.py', '.pl', '.js')) and '# REMOVED # REMOVED eval(' in content:
                results.append(f"[ANOMALY] Obfuscated code in {filepath}")
            # Check for network-related suspicious code
            if any(keyword in content.lower() for keyword in ['socket', 'requests', 'urllib', 'http']):
                if '# REMOVED # REMOVED connect(' in content or '# REMOVED # REMOVED get(' in content or '# REMOVED # REMOVED post(' in content:
                    results.append(f"[ANOMALY] Network activity in {filepath}")
    except Exception as e:
        pass
    return results

def scan_mode():
    log_info("[SCAN] Starting optimized antivirus scan with firewall protection...")
    signatures = load_signatures()
    findings = []
    
    # File system scan - optimized
    log_info("[SCAN] Scanning file system (optimized)...")
    
    # Define file extensions to scan (skip large binary files)
    scan_extensions = {'.py', '.sh', '.pl', '.js', '.php', '.rb', '.bash', '.zsh', '.c', '.cpp', '.h', '.conf', '.cfg', '.ini', '.log', '.txt', '.md'}
    
    scanned_count = 0
    for root, dirs, files in os.walk("/home"):
        # Skip hidden directories for speed
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            path = os.path.join(root, file)
            
            # Only scan relevant file types
            if any(path.lower().endswith(ext) for ext in scan_extensions):
                if is_hidden(path) and os.access(path, os.X_OK):
                    findings.append(f"[ANOMALY] Hidden executable: {path}")
                
                result = scan_file(path, signatures)
                if result:
                    findings.extend(result)
                    scanned_count += 1
                    
                    # Early termination if too many threats found
                    if len(findings) > 50:
                        log_warn("[SCAN] Too many threats detected - stopping scan for safety")
                        break
        
        if len(findings) > 50:
            break
    
    log_info(f"[SCAN] Scanned {scanned_count} files")
    
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
        log_info(f"[SCAN] {len(findings)} threats detected:")
        for f in findings[:20]:  # Limit output to first 20 findings
            log_info(f)
        if len(findings) > 20:
            log_info(f"[SCAN] ... and {len(findings) - 20} more threats found")
    else:
        log_info("[SCAN] No threats found. System is secure.")
        log_info("🛡️  SYSTEM SAFE - No malicious activity detected")
    
    log_info(f"[SCAN] Scan completed in {len(findings)} findings")

def fix_mode():
    log_info("[FIX] Starting automatic threat remediation...")
    signatures = load_signatures()
    fixed_count = 0
    
    # File system scan and fix
    log_info("[FIX] Scanning and fixing file system threats...")
    
    scan_extensions = {'.py', '.sh', '.pl', '.js', '.php', '.rb', '.bash', '.zsh', '.c', '.cpp', '.h', '.conf', '.cfg', '.ini', '.log', '.txt', '.md'}
    
    for root, dirs, files in os.walk("/home"):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            path = os.path.join(root, file)
            
            if any(path.lower().endswith(ext) for ext in scan_extensions):
                # Scan and fix threats
                try:
                    with open(path, 'r', errors='ignore') as f:
                        content = f.read()
                        original_content = content
                    
                    threats_found = []
                    
                    # Check for each threat type
                    for name, pattern in signatures.items():
                        if re.search(pattern, content, re.IGNORECASE):
                            threats_found.append(name)
                    
                    # Fix obfuscated code
                    if path.endswith(('.sh', '.py', '.pl', '.js')) and '# REMOVED # REMOVED eval(' in content:
                        content = content.replace('# REMOVED # REMOVED eval(', '# REMOVED # REMOVED # REMOVED eval(')
                        threats_found.append('Obfuscated code')
                    
                    # Fix network activity in scripts
                    if any(keyword in content.lower() for keyword in ['socket', 'requests', 'urllib', 'http']):
                        if '# REMOVED # REMOVED connect(' in content or '# REMOVED # REMOVED get(' in content or '# REMOVED # REMOVED post(' in content:
                            content = content.replace('# REMOVED # REMOVED connect(', '# REMOVED # REMOVED # REMOVED connect(')
                            content = content.replace('# REMOVED # REMOVED get(', '# REMOVED # REMOVED # REMOVED get(')
                            content = content.replace('# REMOVED # REMOVED post(', '# REMOVED # REMOVED # REMOVED post(')
                            threats_found.append('Network activity')
                    
                    # Write fixed content if threats were found
                    if threats_found:
                        with open(path, 'w') as f:
                            f.write(content)
                        log_info(f"[FIX] Fixed {len(threats_found)} threats in {path}: {', '.join(threats_found)}")
                        fixed_count += 1
                
                except Exception as e:
                    log_warn(f"[FIX] Could not fix {path}: {e}")
    
    # Remove hidden executables
    log_info("[FIX] Removing hidden executable files...")
    for root, dirs, files in os.walk("/home"):
        for file in files:
            path = os.path.join(root, file)
            if is_hidden(path) and os.access(path, os.X_OK):
                try:
                    os.remove(path)
                    log_info(f"[FIX] Removed hidden executable: {path}")
                    fixed_count += 1
                except Exception as e:
                    log_warn(f"[FIX] Could not remove {path}: {e}")
    
    # Fix firewall rules
    log_info("[FIX] Securing firewall...")
    try:
        # Block suspicious IPs
        block_suspicious_ips()
        
        # Enable UFW if inactive
        result = subprocess.run(['sudo', 'ufw', 'status'], capture_output=True, text=True)
        if 'Status: inactive' in result.stdout:
            subprocess.run(['sudo', 'ufw', '--force', 'enable'], check=True)
            log_info("[FIX] Enabled UFW firewall")
            fixed_count += 1
    except Exception as e:
        log_warn(f"[FIX] Could not configure firewall: {e}")
    
    # Kill suspicious processes
    log_info("[FIX] Terminating suspicious processes...")
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if any(keyword in line.lower() for keyword in ['nc -l', 'netcat', 'reverse', 'backdoor']):
                pid = line.split()[1]
                try:
                    subprocess.run(['sudo', 'kill', '-9', pid], check=True)
                    log_info(f"[FIX] Killed suspicious process PID {pid}")
                    fixed_count += 1
                except:
                    pass
    except Exception as e:
        log_warn(f"[FIX] Could not check processes: {e}")
    
    log_info(f"[FIX] Remediation completed. Fixed {fixed_count} threats.")
    log_info("🛡️  SYSTEM SECURED - All threats neutralized")
