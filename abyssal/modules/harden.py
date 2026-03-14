import subprocess
import os
from modules.logs import log_info, log_warn

def run_command(cmd, description, check=True):
    """Helper function to run commands with proper error handling"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=check)
        log_info(f"[HARDEN] {description} completed successfully.")
        return result.stdout
    except subprocess.CalledProcessError as e:
        log_warn(f"[HARDEN] {description} failed: {e}")
        return None
    except Exception as e:
        log_warn(f"[HARDEN] {description} error: {e}")
        return None

def harden_mode():
    log_info("[HARDEN] Starting system hardening...")
    
    # Check if Lynis is available
    lynis_available = run_command(['which', 'lynis'], 'Checking for Lynis', check=False)
    
    if lynis_available:
        log_info("[HARDEN] Running Lynis system audit...")
        output = run_command(['sudo', 'lynis', 'audit', 'system', '--quiet'], 'Lynis audit')
        if output:
            summary = []
            capture = False
            for line in output.splitlines():
                if any(keyword in line for keyword in ['Hardening index', 'Suggestions', 'Warnings', 'Test results']):
                    capture = True
                if capture and line.strip():
                    summary.append(line)
                if capture and '==' in line and len(summary) > 5:
                    break
            
            if summary:
                log_info("[HARDEN] Lynis summary:")
                for line in summary[-10:]:  # Show last 10 relevant lines
                    log_info(line)
            else:
                log_info("[HARDEN] Lynis completed. Check /var/log/lynis.log for details.")
    else:
        log_warn("[HARDEN] Lynis not found. Install with: sudo apt install lynis")
        log_info("[HARDEN] Performing basic hardening checks...")
        
        # Basic security checks
        basic_checks = [
            (['sudo', 'ufw', 'status'], 'Checking firewall status'),
            (['sudo', 'fail2ban-client', 'status'], 'Checking fail2ban status'),
            (['sudo', 'systemctl', 'status', 'ssh'], 'Checking SSH service'),
        ]
        
        for cmd, desc in basic_checks:
            run_command(cmd, desc, check=False)
    
    # Additional hardening tasks
    log_info("[HARDEN] Applying security configurations...")
    
    # Set secure file permissions
    try:
        # Secure critical files
        critical_files = [
            '/etc/passwd',
            '/etc/shadow', 
            '/etc/group',
            '/etc/gshadow'
        ]
        
        for file_path in critical_files:
            if os.path.exists(file_path):
                if 'shadow' in file_path:
                    run_command(['sudo', 'chmod', '600', file_path], f'Securing {file_path}')
                else:
                    run_command(['sudo', 'chmod', '644', file_path], f'Securing {file_path}')
    except Exception as e:
        log_warn(f"[HARDEN] Failed to secure file permissions: {e}")
    
    # Check for world-writable files
    log_info("[HARDEN] Checking for world-writable files...")
    try:
        result = subprocess.run(['find', '/', '-type', 'f', '-perm', '-002', '2>/dev/null'], 
                              capture_output=True, text=True, shell=True)
        if result.stdout.strip():
            files = result.stdout.strip().split('\n')[:10]  # Limit to first 10
            log_warn("[HARDEN] World-writable files found:")
            for file_path in files:
                if file_path.strip():
                    log_warn(f"[HARDEN] {file_path}")
        else:
            log_info("[HARDEN] No world-writable files found in critical areas.")
    except Exception as e:
        log_warn(f"[HARDEN] Could not check world-writable files: {e}")
    
    # SSH hardening recommendations
    log_info("[HARDEN] SSH security recommendations...")
    try:
        ssh_config = '/etc/ssh/sshd_config'
        if os.path.exists(ssh_config):
            with open(ssh_config, 'r') as f:
                content = f.read()
            
            recommendations = []
            if 'PermitRootLogin yes' in content:
                recommendations.append("Set 'PermitRootLogin no' in SSH config")
            if 'PasswordAuthentication yes' in content:
                recommendations.append("Consider 'PasswordAuthentication no' (use SSH keys)")
            if '#Port 22' in content or 'Port 22' in content:
                recommendations.append("Consider changing default SSH port from 22")
            
            if recommendations:
                log_info("[HARDEN] SSH hardening recommendations:")
                for rec in recommendations:
                    log_info(f"[HARDEN] - {rec}")
            else:
                log_info("[HARDEN] SSH configuration appears secure.")
    except Exception as e:
        log_warn(f"[HARDEN] Could not analyze SSH config: {e}")
    
    # System update check
    log_info("[HARDEN] Checking for system updates...")
    try:
        run_command(['sudo', 'apt', 'update'], 'Updating package lists', check=False)
        result = run_command(['sudo', 'apt', 'list', '--upgradable'], 'Checking upgrades', check=False)
        if result and 'upgradable' in result:
            log_info("[HARDEN] System updates available. Run: sudo apt upgrade")
        else:
            log_info("[HARDEN] System is up to date.")
    except Exception as e:
        log_warn(f"[HARDEN] Could not check for updates: {e}")
    
    log_info("[HARDEN] System hardening completed.")
