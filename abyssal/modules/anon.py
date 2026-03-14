import subprocess
import random
import string
import time
import os
from modules.logs import log_info, log_warn

def random_hostname():
    ts = int(time.time())
    rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"abyssal-{rand}-{ts}"

def check_service_status(service_name):
    """Check if a service is running"""
    try:
        result = subprocess.run(['systemctl', 'is-active', service_name], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def anon_mode():
    log_info("[ANON] Starting anonymity mode...")
    
    # Start Tor service
    log_info("[ANON] Configuring Tor service...")
    try:
        if not check_service_status('tor'):
            subprocess.run(["sudo", "systemctl", "start", "tor"], check=True)
            log_info("[ANON] Tor service started.")
        else:
            log_info("[ANON] Tor service already running.")
    except Exception as e:
        log_warn(f"[ANON] Failed to start Tor: {e}")
        log_warn("[ANON] Install Tor with: sudo apt install tor")
    
    # Randomize MAC address (check if interface exists first)
    log_info("[ANON] Checking network interfaces...")
    try:
        # Get available network interfaces
        result = subprocess.run(['ip', 'link', 'show'], capture_output=True, text=True)
        interfaces = []
        for line in result.stdout.split('\n'):
            if ': ' in line and not line.startswith(' '):
                interface = line.split(':')[1].strip().split('@')[0]
                if interface not in ['lo']:
                    interfaces.append(interface)
        
        for interface in interfaces[:2]:  # Limit to first 2 non-loopback interfaces
            try:
                subprocess.run(["sudo", "macchanger", "-r", interface], check=True)
                log_info(f"[ANON] MAC address randomized on {interface}.")
            except Exception as e:
                log_warn(f"[ANON] Failed to randomize MAC on {interface}: {e}")
                log_warn("[ANON] Install macchanger with: sudo apt install macchanger")
    except Exception as e:
        log_warn(f"[ANON] Failed to detect network interfaces: {e}")
    
    # Change hostname
    log_info("[ANON] Changing hostname...")
    try:
        new_host = random_hostname()
        subprocess.run(["sudo", "hostnamectl", "set-hostname", new_host], check=True)
        log_info(f"[ANON] Hostname changed to {new_host}.")
        
        # Update /etc/hosts file
        with open('/etc/hosts', 'r') as f:
            hosts_content = f.read()
        
        # Backup original hosts file
        subprocess.run(['sudo', 'cp', '/etc/hosts', '/etc/hosts.backup'], check=True)
        
        # Update localhost entries
        new_hosts = hosts_content.replace('127.0.1.1\t' + os.uname()[1], 
                                        f'127.0.1.1\t{new_host}')
        
        with open('/tmp/hosts_new', 'w') as f:
            f.write(new_hosts)
        
        subprocess.run(['sudo', 'mv', '/tmp/hosts_new', '/etc/hosts'], check=True)
        log_info("[ANON] Updated /etc/hosts file.")
        
    except Exception as e:
        log_warn(f"[ANON] Failed to change hostname: {e}")
    
    # Flush DNS cache
    log_info("[ANON] Flushing DNS cache...")
    try:
        # Try different methods based on system
        subprocess.run(["sudo", "systemd-resolve", "--flush-caches"], check=True)
        log_info("[ANON] DNS cache flushed (systemd-resolved).")
    except:
        try:
            subprocess.run(["sudo", "resolvectl", "flush-caches"], check=True)
            log_info("[ANON] DNS cache flushed (resolvectl).")
        except:
            try:
                subprocess.run(["sudo", "service", "dnsmasq", "restart"], check=True)
                log_info("[ANON] DNS service restarted (dnsmasq).")
            except:
                log_warn("[ANON] Could not flush DNS cache.")
    
    # Clear temporary files and bash history
    log_info("[ANON] Cleaning up traces...")
    try:
        # Clear bash history
        subprocess.run(["history", "-c"], shell=True)
        subprocess.run(["rm", "-f", os.path.expanduser("~/.bash_history")], check=True)
        log_info("[ANON] Bash history cleared.")
        
        # Clear temporary files
        subprocess.run(["sudo", "rm", "-rf", "/tmp/*"], check=True)
        log_info("[ANON] Temporary files cleared.")
    except Exception as e:
        log_warn(f"[ANON] Failed to clean traces: {e}")
    
    log_info("[ANON] Anonymity configuration completed.")
