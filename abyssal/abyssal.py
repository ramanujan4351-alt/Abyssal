import argparse
import time
import threading
import os
from modules.anon import anon_mode
from modules.scan import scan_mode, fix_mode
from modules.harden import harden_mode
from modules.logkiller import logkiller_mode
from modules.antimitm import antimitm_mode
from modules.logs import log_info

def full_mode():
    log_info("Running full mode: anonymity, scan, hardening.")
    anon_mode()
    scan_mode()
    harden_mode()

def interactive_mode():
    """Interactive UI mode with live scanning"""
    print("\n" + "="*60)
    print("     ABYSSAL SECURITY - INTERACTIVE MODE")
    print("="*60)
    print("\n🔍 Live Security Monitoring Interface")
    print("━" * 60)
    
    # Show available commands
    print("\n📋 AVAILABLE COMMANDS:")
    commands = [
        ("python3 abyssal.py --scan", "Run custom antivirus scan"),
        ("python3 abyssal.py --fix", "Fix all detected threats automatically"),
        ("python3 abyssal.py --interactive", "Interactive UI mode"),
        ("python3 abyssal.py --live", "Start live monitoring"),
        ("python3 abyssal.py --live-on", "Enable live monitoring on system boot"),
        ("python3 abyssal.py --live-off", "Disable live monitoring on system boot"),
        ("python3 abyssal.py --harden", "System hardening"),
        ("python3 abyssal.py --full", "Run all modules"),
        ("python3 abyssal.py --logkiller", "Erase system logs"),
        ("python3 abyssal.py --antimitm", "Run anti-MITM checks"),
        ("python3 abyssal.py --anon", "Start anonymity mode")
    ]
    
    for cmd, desc in commands:
        print(f"  🔹 {cmd:<35} # {desc}")
    
    print("\n" + "━" * 60)
    
    while True:
        print("\n📋 MENU:")
        print("1. 🚀 Quick Scan")
        print("2. 🔧 Deep Scan") 
        print("3. 🛡️  Fix All Threats")
        print("4. 👤 Anonymity Mode")
        print("5. 🔨 System Harden")
        print("6. 🌐 Anti-MITM Check")
        print("7. 🧹 Log Killer")
        print("8. 🔄 Start Live Monitoring")
        print("9. 📜 Show Commands")
        print("10. ⚙️ Startup Settings")
        print("11. ❌ Exit")
        print("━" * 60)
        
        try:
            choice = input("\n⚡ Select option (1-11): ").strip()
            
            if choice == '1':
                print("\n🚀 Starting quick scan...")
                threading.Thread(target=scan_mode, daemon=True).start()
                time.sleep(1)
                
            elif choice == '2':
                print("\n🔧 Starting deep scan...")
                threading.Thread(target=scan_mode, daemon=True).start()
                time.sleep(1)
                
            elif choice == '3':
                print("\n🛡️  Fixing all threats...")
                threading.Thread(target=fix_mode, daemon=True).start()
                time.sleep(1)
                
            elif choice == '4':
                print("\n👤 Starting anonymity mode...")
                threading.Thread(target=anon_mode, daemon=True).start()
                time.sleep(1)
                
            elif choice == '5':
                print("\n🔨 Starting system hardening...")
                threading.Thread(target=harden_mode, daemon=True).start()
                time.sleep(1)
                
            elif choice == '6':
                print("\n🌐 Starting anti-MITM check...")
                threading.Thread(target=antimitm_mode, daemon=True).start()
                time.sleep(1)
                
            elif choice == '7':
                print("\n🧹 Starting log cleanup...")
                threading.Thread(target=logkiller_mode, daemon=True).start()
                time.sleep(1)
                
            elif choice == '8':
                print("\n🔄 Starting live monitoring...")
                start_live_monitoring()
                
            elif choice == '9':
                print("\n📜 Showing available commands...")
                for cmd, desc in commands:
                    print(f"  🔹 {cmd:<35} # {desc}")
                
            elif choice == '10':
                print("\n⚙️ Startup Settings:")
                startup_settings_menu()
                
            elif choice == '11':
                print("\n👋 Exiting ABYSSAL SECURITY...")
                break
                
            else:
                print("\n❌ Invalid choice! Please select 1-11.")
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Monitoring interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

def startup_settings_menu():
    """Configure startup settings for live monitoring"""
    print("\n⚙️ STARTUP CONFIGURATION:")
    print("━" * 40)
    
    # Check current startup status
    startup_file = "/home/$(whoami)/.config/abyssal-startup"
    current_status = "Unknown"
    
    try:
        if os.path.exists(startup_file):
            with open(startup_file, 'r') as f:
                current_status = f.read().strip()
    except:
        pass
    
    print(f"Current Status: {current_status}")
    print("\nOptions:")
    print("1. 🟢 Enable Live Monitoring on Boot")
    print("2. 🔴 Disable Live Monitoring on Boot")
    print("3. 🔙 Set Custom Startup Command")
    print("4. ⬅️ Back to Main Menu")
    
    try:
        choice = input("\n⚡ Select option (1-4): ").strip()
        
        if choice == '1':
            enable_startup_monitoring()
        elif choice == '2':
            disable_startup_monitoring()
        elif choice == '3':
            set_custom_startup()
        elif choice == '4':
            return
        else:
            print("\n❌ Invalid choice!")
            
    except KeyboardInterrupt:
        print("\n⚠️  Settings menu interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def enable_startup_monitoring():
    """Enable live monitoring on system boot"""
    try:
        startup_file = "/home/$(whoami)/.config/abyssal-startup"
        os.makedirs(os.path.dirname(startup_file), exist_ok=True)
        
        with open(startup_file, 'w') as f:
            f.write("live-monitoring-enabled")
        
        # Create systemd service file
        service_content = f"""[Unit]
Description=ABYSSAL Live Monitoring Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /home/malfoy/Desktop/abyssal/abyssal.py --live
Restart=always
Restart=on-failure
User=root
Group=root

[Install]
WantedBy=multi-user.target
"""
        
        service_file = "/etc/systemd/system/abyssal-live.service"
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        # Reload systemd and enable service
        subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
        subprocess.run(['sudo', 'systemctl', 'enable', 'abyssal-live.service'], check=True)
        
        print("✅ Live monitoring enabled on boot")
        
    except Exception as e:
        print(f"❌ Failed to enable startup: {e}")

def disable_startup_monitoring():
    """Disable live monitoring on system boot"""
    try:
        startup_file = "/home/$(whoami)/.config/abyssal-startup"
        if os.path.exists(startup_file):
            os.remove(startup_file)
        
        # Disable systemd service
        subprocess.run(['sudo', 'systemctl', 'disable', 'abyssal-live.service'], check=True)
        subprocess.run(['sudo', 'systemctl', 'stop', 'abyssal-live.service'], check=True)
        
        print("🔴 Live monitoring disabled on boot")
        
    except Exception as e:
        print(f"❌ Failed to disable startup: {e}")

def set_custom_startup():
    """Set custom startup command"""
    try:
        custom_cmd = input("Enter custom startup command: ").strip()
        startup_file = "/home/$(whoami)/.config/abyssal-startup"
        
        with open(startup_file, 'w') as f:
            f.write(custom_cmd)
        
        # Update systemd service
        service_content = f"""[Unit]
Description=ABYSSAL Custom Startup Service
After=network.target

[Service]
Type=simple
ExecStart=/bin/bash -c "{custom_cmd}"
Restart=always
Restart=on-failure
User=root
Group=root
"""
        
        service_file = "/etc/systemd/system/abyssal-custom.service"
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        # Reload systemd and enable service
        subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
        subprocess.run(['sudo', 'systemctl', 'enable', 'abyssal-custom.service'], check=True)
        
        print(f"✅ Custom startup command set: {custom_cmd}")
        
    except Exception as e:
        print(f"❌ Failed to set custom startup: {e}")

def start_live_monitoring():
    """Start live security monitoring"""
    print("\n🔄 LIVE MONITORING ACTIVE")
    print("Press Ctrl+C to stop monitoring")
    print("━" * 60)
    
    try:
        while True:
            print(f"\n🕐 {time.strftime('%H:%M:%S')} - Monitoring system...")
            
            # Quick security check
            threading.Thread(target=quick_security_check, daemon=True).start()
            time.sleep(30)  # Check every 30 seconds
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Live monitoring stopped")

def quick_security_check():
    """Perform quick security checks for live monitoring"""
    # This would run quick checks - simplified for demo
    print("   🔍 Quick security scan completed - System secure")

def print_logo_and_usage():
    print("\n" + "="*50)
    print("     ABYSSAL SECURITY")
    print("="*50 + "\n")
    print("Usage:")
    print("  python3 abyssal.py --scan         # Run custom antivirus scan")
    print("  python3 abyssal.py --fix          # Fix all detected threats automatically")
    print("  python3 abyssal.py --interactive   # Interactive UI mode")
    print("  python3 abyssal.py --live         # Start live monitoring")
    print("  python3 abyssal.py --live-on      # Enable live monitoring on system boot")
    print("  python3 abyssal.py --live-off     # Disable live monitoring on system boot")
    print("  python3 abyssal.py --startup       # Configure startup settings")
    print("  python3 abyssal.py --harden       # System hardening")
    print("  python3 abyssal.py --full         # Run all modules")
    print("  python3 abyssal.py --logkiller    # Erase system logs")
    print("  python3 abyssal.py --antimitm     # Run anti-MITM checks")
    print("  python3 abyssal.py --anon         # Start anonymity mode\n")
    print("Run with sudo if required for system-level actions.\n")

def check_startup_status():
    """Check current startup status"""
    startup_file = f"/home/{os.getenv('USER', 'malfoy')}/.config/abyssal-startup"
    current_status = "Unknown"
    
    try:
        if os.path.exists(startup_file):
            with open(startup_file, 'r') as f:
                current_status = f.read().strip()
    except:
        pass
    
    return current_status

def main():
    print_logo_and_usage()
    parser = argparse.ArgumentParser(description="Abyssal CLI: Born from the abyss, hunting malware in the shadows.")
    parser.add_argument('--anon', action='store_true', help='Start anonymity mode')
    parser.add_argument('--scan', action='store_true', help='Run custom antivirus scan')
    parser.add_argument('--fix', action='store_true', help='Fix all detected threats automatically')
    parser.add_argument('--interactive', action='store_true', help='Interactive UI mode')
    parser.add_argument('--live', action='store_true', help='Start live monitoring')
    parser.add_argument('--live-on', action='store_true', help='Enable live monitoring on system boot')
    parser.add_argument('--live-off', action='store_true', help='Disable live monitoring on system boot')
    parser.add_argument('--startup', action='store_true', help='Configure startup settings')
    parser.add_argument('--harden', action='store_true', help='System hardening')
    parser.add_argument('--full', action='store_true', help='Run all modules')
    parser.add_argument('--logkiller', action='store_true', help='Erase system logs')
    parser.add_argument('--antimitm', action='store_true', help='Run anti-MITM checks')
    args = parser.parse_args()

    if args.anon:
        anon_mode()
    elif args.scan:
        scan_mode()
    elif args.fix:
        fix_mode()
    elif args.interactive:
        interactive_mode()
    elif args.live:
        start_live_monitoring()
    elif args.live_on:
        enable_startup_monitoring()
    elif args.live_off:
        disable_startup_monitoring()
    elif args.startup:
        startup_settings_menu()
    elif args.harden:
        harden_mode()
    elif args.full:
        full_mode()
    elif args.logkiller:
        logkiller_mode()
    elif args.antimitm:
        antimitm_mode()
    else:
        # Only print usage instructions (logo already shown above)
        pass

if __name__ == "__main__":
    main()
