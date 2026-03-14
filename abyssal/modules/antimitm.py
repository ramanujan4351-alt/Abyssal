import subprocess
from modules.logs import log_info, log_warn

def antimitm_mode():
    log_info("[ANTIMITM] Running anti-MITM checks...")
    try:
        # Check for ARP spoofing
        arp_out = subprocess.check_output(['arp', '-a'], text=True)
        suspicious = []
        for line in arp_out.splitlines():
            if 'incomplete' in line or line.count('.') > 3:
                suspicious.append(line)
        if suspicious:
            log_warn("[ANTIMITM] Suspicious ARP entries detected:")
            for s in suspicious:
                log_warn(f"[ANTIMITM] {s}")
        else:
            log_info("[ANTIMITM] No suspicious ARP entries found.")
    except Exception as e:
        log_warn(f"[ANTIMITM] ARP check failed: {e}")
    try:
        # Check for DNS poisoning (compare /etc/resolv.conf to known good DNS)
        with open('/etc/resolv.conf') as f:
            resolv = f.read()
        if 'nameserver 8.8.8.8' not in resolv and 'nameserver 1.1.1.1' not in resolv:
            log_warn("[ANTIMITM] DNS servers are not standard public resolvers. Possible MITM?")
        else:
            log_info("[ANTIMITM] DNS servers appear normal.")
    except Exception as e:
        log_warn(f"[ANTIMITM] DNS check failed: {e}")
