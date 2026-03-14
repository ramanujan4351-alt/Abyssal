import subprocess
import re
import socket
from modules.logs import log_info, log_warn

def run_command(cmd, description, check=True):
    """Helper function to run commands with proper error handling"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=check)
        return result.stdout
    except subprocess.CalledProcessError as e:
        log_warn(f"[ANTIMITM] {description} failed: {e}")
        return None
    except Exception as e:
        log_warn(f"[ANTIMITM] {description} error: {e}")
        return None

def check_arp_spoofing():
    """Check for ARP spoofing attacks"""
    log_info("[ANTIMITM] Checking for ARP spoofing...")
    suspicious = []
    
    arp_output = run_command(['arp', '-a'], 'ARP table scan', check=False)
    if arp_output:
        lines = arp_output.splitlines()
        mac_addresses = {}
        
        for line in lines:
            # Parse ARP entry
            match = re.search(r'(\d+\.\d+\.\d+\.\d+)\s+([0-9a-fA-F:-]+)', line)
            if match:
                ip, mac = match.groups()
                if mac in mac_addresses:
                    # Same MAC address for multiple IPs - suspicious
                    if ip not in mac_addresses[mac]:
                        suspicious.append(f"[ARP] MAC {mac} associated with multiple IPs: {mac_addresses[mac]}, {ip}")
                else:
                    mac_addresses[mac] = [ip]
                
                # Check for incomplete entries
                if 'incomplete' in line.lower():
                    suspicious.append(f"[ARP] Incomplete ARP entry: {line.strip()}")
                
                # Check for multicast MACs on unicast IPs
                if mac.startswith('01:00:5e') or mac.startswith('ff:ff:ff'):
                    suspicious.append(f"[ARP] Multicast MAC for unicast IP: {ip} -> {mac}")
    
    return suspicious

def check_dns_poisoning():
    """Check for DNS poisoning"""
    log_info("[ANTIMITM] Checking for DNS poisoning...")
    issues = []
    
    try:
        # Read current DNS servers
        with open('/etc/resolv.conf', 'r') as f:
            resolv_content = f.read()
        
        dns_servers = []
        for line in resolv_content.splitlines():
            if line.startswith('nameserver'):
                dns_servers.append(line.split()[1])
        
        # Check for suspicious DNS servers
        suspicious_dns = ['127.0.0.1', '0.0.0.0']
        public_dns = ['8.8.8.8', '1.1.1.1', '9.9.9.9', '208.67.222.222']
        
        if not any(dns in dns_servers for dns in public_dns):
            if all(dns not in dns_servers for dns in suspicious_dns):
                issues.append(f"[DNS] No standard public DNS servers found. Current: {dns_servers}")
        
        # Check for localhost being the only DNS (could be DNS tunneling)
        if dns_servers == ['127.0.0.1']:
            issues.append("[DNS] Only localhost DNS configured - possible DNS tunneling")
        
        # Test DNS resolution to known good domains
        test_domains = ['google.com', 'github.com', 'stackoverflow.com']
        for domain in test_domains:
            try:
                resolved = socket.gethostbyname(domain)
                # Check if resolving to suspicious IPs
                if resolved.startswith('127.') or resolved.startswith('0.'):
                    issues.append(f"[DNS] {domain} resolving to local IP: {resolved}")
            except:
                issues.append(f"[DNS] Failed to resolve {domain}")
    
    except Exception as e:
        issues.append(f"[DNS] Could not analyze DNS configuration: {e}")
    
    return issues

def check_network_interfaces():
    """Check for suspicious network interfaces"""
    log_info("[ANTIMITM] Checking network interfaces...")
    issues = []
    
    # Get network interfaces
    ip_output = run_command(['ip', 'link', 'show'], 'Network interface scan', check=False)
    if ip_output:
        interfaces = []
        for line in ip_output.splitlines():
            if ': ' in line and not line.startswith(' '):
                interface = line.split(':')[1].strip().split('@')[0]
                if interface not in ['lo']:
                    interfaces.append(interface)
        
        # Check for promiscuous mode
        for interface in interfaces:
            promisc_output = run_command(['ip', 'link', 'show', interface], f'Checking {interface}', check=False)
            if promisc_output and 'PROMISC' in promisc_output:
                issues.append(f"[INTERFACE] {interface} is in promiscuous mode - possible sniffing")
    
    return issues

def check_routing_table():
    """Check routing table for suspicious routes"""
    log_info("[ANTIMITM] Checking routing table...")
    issues = []
    
    route_output = run_command(['ip', 'route', 'show'], 'Route table scan', check=False)
    if route_output:
        for line in route_output.splitlines():
            # Check for default routes to suspicious gateways
            if 'default via' in line:
                gateway = re.search(r'default via (\d+\.\d+\.\d+\.\d+)', line)
                if gateway:
                    gw_ip = gateway.group(1)
                    # Check if gateway is on local network but not standard
                    if gw_ip.startswith('192.168.') or gw_ip.startswith('10.') or gw_ip.startswith('172.'):
                        if not any(gw_ip.startswith(prefix) for prefix in ['192.168.1', '192.168.0', '10.0.0']):
                            issues.append(f"[ROUTE] Unusual default gateway: {gw_ip}")
    
    return issues

def check_active_connections():
    """Check active network connections for suspicious activity"""
    log_info("[ANTIMITM] Checking active connections...")
    issues = []
    
    # Get active connections
    conn_output = run_command(['ss', '-tuln'], 'Connection scan', check=False)
    if conn_output:
        for line in conn_output.splitlines():
            # Check for services on unusual ports
            if 'LISTEN' in line or 'ESTABLISHED' in line:
                # Extract port number
                port_match = re.search(r':(\d+)\s', line)
                if port_match:
                    port = int(port_match.group(1))
                    # Suspicious ports commonly used in attacks
                    suspicious_ports = [4444, 5555, 6666, 7777, 8888, 9999, 31337, 12345, 54321]
                    if port in suspicious_ports:
                        issues.append(f"[CONNECTION] Service on suspicious port: {line.strip()}")
    
    return issues

def antimitm_mode():
    log_info("[ANTIMITM] Starting comprehensive anti-MITM analysis...")
    
    all_issues = []
    
    # Run all checks
    all_issues.extend(check_arp_spoofing())
    all_issues.extend(check_dns_poisoning())
    all_issues.extend(check_network_interfaces())
    all_issues.extend(check_routing_table())
    all_issues.extend(check_active_connections())
    
    # Report findings
    if all_issues:
        log_warn("[ANTIMITM] Potential MITM indicators detected:")
        for issue in all_issues:
            log_warn(issue)
        
        # Provide recommendations
        log_info("[ANTIMITM] Recommendations:")
        log_info("[ANTIMITM] - Monitor ARP tables regularly")
        log_info("[ANTIMITM] - Use static ARP entries for critical infrastructure")
        log_info("[ANTIMITM] - Configure trusted DNS servers")
        log_info("[ANTIMITM] - Enable DHCP snooping on managed switches")
        log_info("[ANTIMITM] - Use VPN for sensitive communications")
    else:
        log_info("[ANTIMITM] No MITM indicators detected. Network appears secure.")
    
    log_info("[ANTIMITM] Anti-MITM analysis completed.")
