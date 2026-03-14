import argparse
import time
import threading
import os
import subprocess
import sys
import re
import json
from modules.anon import anon_mode
from modules.scan import scan_mode, fix_mode
from modules.harden import harden_mode
from modules.logkiller import logkiller_mode
from modules.antimitm import antimitm_mode
from modules.logs import log_info

# Configuration
CONFIG_DIR = f"/home/{os.getenv('USER', 'malfoy')}/.config/abyssal"
os.makedirs(CONFIG_DIR, exist_ok=True)

def get_feature_state(feature):
    """Get current state of a feature"""
    feature_file = f"{CONFIG_DIR}/{feature}-state"
    try:
        if os.path.exists(feature_file):
            with open(feature_file, 'r') as f:
                return f.read().strip()
    except:
        pass
    return 'on'  # Default to on

def set_feature_state(feature, state):
    """Set state of a feature"""
    feature_file = f"{CONFIG_DIR}/{feature}-state"
    try:
        with open(feature_file, 'w') as f:
            f.write(state)
        return True
    except:
        return False

def clear_screen():
    """Clear terminal screen"""
    os.system('clear' if os.name == 'posix' else 'cls')

def run_with_sudo(func, func_name):
    """Run function with sudo if needed"""
    sudo_funcs = ['harden_mode', 'logkiller_mode', 'fix_mode', 'antimitm_mode']
    
    if func_name in sudo_funcs:
        print(f"⚠️  {func_name.replace('_', ' ').title()} requires sudo")
        try:
            result = subprocess.run(['sudo', 'python3', '-c', f'''
import sys
sys.path.insert(0, "{os.path.dirname(os.path.abspath(__file__))}")
from modules.{func_name.replace("_mode", "")} import {func_name}
{func_name}()
'''], check=True)
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    else:
        try:
            func()
            return True
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False

def show_banner():
    """Show ABYSSAL banner"""
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                    ABYSSAL SECURITY                          ║")
    print("║                 ADVANCED SECURITY TOOLKIT                  ║")
    print("╚══════════════════════════════════════════════════════════════╝")

def main_menu():
    """Main interactive menu"""
    while True:
        clear_screen()
        show_banner()
        
        # Status bar
        enabled = sum(1 for f in ['scan', 'fix', 'anon', 'harden', 'antimitm', 'logkiller', 'live', 'full'] if get_feature_state(f) == 'on')
        print(f"📊 Active Features: {enabled}/8 | 🕐 {time.strftime('%H:%M:%S')}")
        print()
        
        # Menu options
        options = [
            ("1️⃣", "🚀", "Quick Scan", "scan_mode"),
            ("2️⃣", "🔧", "Deep Scan", "scan_mode"),
            ("3️⃣", "🛡️", "Fix All Threats", "fix_mode"),
            ("4️⃣", "👤", "Anonymity Mode", "anon_mode"),
            ("5️⃣", "🔨", "System Harden", "harden_mode"),
            ("6️⃣", "🌐", "Anti-MITM", "antimitm_mode"),
            ("7️⃣", "🧹", "Log Killer", "logkiller_mode"),
            ("8️⃣", "🔄", "Live Monitor", "start_live_monitoring"),
            ("9️⃣", "⚙️", "Feature Control", "feature_menu"),
            ("🔟", "⚙️", "Startup Settings", "startup_menu"),
            ("1️⃣0️⃣", "🔙", "Exit", "sys.exit")
        ]
        
        # Display menu
        print("┌─────────────────────────────────────────────────────────────────┐")
        print("│                    MAIN MENU                             │")
        print("├─────────────────────────────────────────────────────────────────┤")
        
        for i in range(0, len(options), 2):
            if i + 1 < len(options):
                opt1, icon1, text1, _ = options[i]
                opt2, icon2, text2, _ = options[i + 1]
                print(f"│ {opt1} {icon1} {text1:<18} {opt2} {icon2} {text2:<18} │")
            else:
                opt1, icon1, text1, _ = options[i]
                print(f"│ {opt1} {icon1} {text1:<47} │")
        
        print("└─────────────────────────────────────────────────────────────────┘")
        
        # Get user choice
        try:
            choice = input("⚡ Select option: ").strip()
            
            # Map choices to functions
            choice_map = {
                '1': ('scan', scan_mode),
                '2': ('scan', scan_mode),
                '3': ('fix', fix_mode),
                '4': ('anon', anon_mode),
                '5': ('harden', harden_mode),
                '6': ('antimitm', antimitm_mode),
                '7': ('logkiller', logkiller_mode),
                '8': ('live', start_live_monitoring),
                '9': feature_menu,
                '10': startup_menu,
                '0': sys.exit
            }
            
            if choice in choice_map:
                feature, func = choice_map[choice]
                
                if callable(func):
                    if feature and get_feature_state(feature) != 'on':
                        print(f"\n❌ {feature.upper()} feature is disabled")
                        input("\n⏸️  Press Enter to continue...")
                        continue
                    
                    print(f"\n🔄 Starting {func.__name__.replace('_', ' ').title()}...")
                    
                    if feature in ['scan', 'anon']:
                        threading.Thread(target=func, daemon=True).start()
                        time.sleep(1)
                        input("\n⏸️  Press Enter to continue...")
                    elif feature == 'live':
                        func()
                    else:
                        success = run_with_sudo(func, func.__name__)
                        input("\n⏸️  Press Enter to continue...")
                else:
                    func()
            else:
                print("\n❌ Invalid option!")
                input("\n⏸️  Press Enter to continue...")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            return  # Use return instead of return
        except Exception as e:
            print(f"\n❌ Error: {e}")
            input("\n⏸️  Press Enter to continue...")

def feature_menu():
    """Feature control menu"""
    while True:
        clear_screen()
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║                   FEATURE CONTROL                           ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print()
        
        features = ['scan', 'fix', 'anon', 'harden', 'antimitm', 'logkiller', 'live', 'full']
        
        print("📊 CURRENT STATUS:")
        print("┌─────────────────────────────────────────────────────────────────┐")
        
        for i, feature in enumerate(features, 1):
            state = get_feature_state(feature)
            status = "🟢 ON" if state == 'on' else "🔴 OFF"
            print(f"│ {i}. {feature.upper():<12}: {status}{' ' * 32}│")
        
        print("└─────────────────────────────────────────────────────────────────┘")
        print()
        
        print("┌─────────────────────────────────────────────────────────────────┐")
        print("│                 CONTROL OPTIONS                           │")
        print("├─────────────────────────────────────────────────────────────────┤")
        print("│ 1️⃣ 🔄 Toggle All       4️⃣ ⚡ Enable Multiple    │")
        print("│ 2️⃣ 🔧 Individual Toggle  5️⃣ ⚡ Disable Multiple    │")
        print("│ 3️⃣ 📊 Show Status       6️⃣ 🔙 Back to Main        │")
        print("└─────────────────────────────────────────────────────────────────┘")
        
        try:
            choice = input("⚡ Select option: ").strip()
            
            if choice == '1':
                toggle_all_features()
            elif choice == '2':
                toggle_individual_feature()
            elif choice == '3':
                show_detailed_status()
            elif choice == '4':
                enable_multiple_features()
            elif choice == '5':
                disable_multiple_features()
            elif choice == '6':
                return
            else:
                print("\n❌ Invalid option!")
                
            input("\n⏸️  Press Enter to continue...")
                
        except KeyboardInterrupt:
            return
        except Exception as e:
            print(f"\n❌ Error: {e}")
            input("\n⏸️  Press Enter to continue...")

def toggle_all_features():
    """Toggle all features on/off"""
    features = ['scan', 'fix', 'anon', 'harden', 'antimitm', 'logkiller', 'live', 'full']
    all_on = all(get_feature_state(f) == 'on' for f in features)
    new_state = 'off' if all_on else 'on'
    
    for feature in features:
        set_feature_state(feature, new_state)
    
    status = "🔴 DISABLED" if new_state == 'off' else "🟢 ENABLED"
    print(f"\n✅ All features {status}")

def toggle_individual_feature():
    """Toggle individual feature"""
    features = ['scan', 'fix', 'anon', 'harden', 'antimitm', 'logkiller', 'live', 'full']
    
    print("\n🔧 SELECT FEATURE TO TOGGLE:")
    for i, feature in enumerate(features, 1):
        state = get_feature_state(feature)
        status = "🟢 ON" if state == 'on' else "🔴 OFF"
        print(f"  {i}. {feature.upper():<12}: {status}")
    
    try:
        choice = input(f"\n⚡ Select feature (1-{len(features)}): ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(features):
            feature = features[int(choice) - 1]
            current_state = get_feature_state(feature)
            new_state = 'off' if current_state == 'on' else 'on'
            
            if set_feature_state(feature, new_state):
                status = "🔴 DISABLED" if new_state == 'off' else "🟢 ENABLED"
                print(f"✅ {feature.upper()} {status}")
            else:
                print(f"❌ Failed to update {feature}")
        else:
            print("❌ Invalid selection!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def show_detailed_status():
    """Show detailed feature status"""
    features = ['scan', 'fix', 'anon', 'harden', 'antimitm', 'logkiller', 'live', 'full']
    
    print("\n📊 DETAILED FEATURE STATUS:")
    print("┌─────────────────────────────────────────────────────────────────┐")
    
    for feature in features:
        state = get_feature_state(feature)
        status = "🟢 ENABLED" if state == 'on' else "🔴 DISABLED"
        print(f"│ {feature.upper():<15}: {status}{' ' * 29}│")
    
    on_count = sum(1 for f in features if get_feature_state(f) == 'on')
    print("├─────────────────────────────────────────────────────────────────┤")
    print(f"│ SUMMARY: {on_count}/{len(features)} features enabled{' ' * 26}│")
    print("└─────────────────────────────────────────────────────────────────┘")

def enable_multiple_features():
    """Enable multiple features"""
    features = ['scan', 'fix', 'anon', 'harden', 'antimitm', 'logkiller', 'live', 'full']
    
    print("\n⚡ ENABLE MULTIPLE FEATURES:")
    for i, feature in enumerate(features, 1):
        print(f"  {i}. {feature}")
    
    try:
        choices = input(f"\n⚡ Enter numbers to enable (comma-separated): ").strip()
        
        if choices:
            selected = [int(x.strip()) for x in choices.split(',') if x.strip().isdigit()]
            enabled = 0
            
            for choice in selected:
                if 1 <= choice <= len(features):
                    feature = features[choice - 1]
                    if set_feature_state(feature, 'on'):
                        enabled += 1
            print(f"✅ Enabled {enabled} features")
        else:
            print("❌ No features selected")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def disable_multiple_features():
    """Disable multiple features"""
    features = ['scan', 'fix', 'anon', 'harden', 'antimitm', 'logkiller', 'live', 'full']
    
    print("\n⚡ DISABLE MULTIPLE FEATURES:")
    for i, feature in enumerate(features, 1):
        print(f"  {i}. {feature}")
    
    try:
        choices = input(f"\n⚡ Enter numbers to disable (comma-separated): ").strip()
        
        if choices:
            selected = [int(x.strip()) for x in choices.split(',') if x.strip().isdigit()]
            disabled = 0
            
            for choice in selected:
                if 1 <= choice <= len(features):
                    feature = features[choice - 1]
                    if set_feature_state(feature, 'off'):
                        disabled += 1
            print(f"✅ Disabled {disabled} features")
        else:
            print("❌ No features selected")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def startup_menu():
    """Startup settings menu"""
    clear_screen()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                   STARTUP SETTINGS                         ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    
    startup_file = f"{CONFIG_DIR}/startup-config"
    current_config = "Unknown"
    
    try:
        if os.path.exists(startup_file):
            with open(startup_file, 'r') as f:
                current_config = f.read().strip()
    except:
        pass
    
    print(f"📊 Current Startup: {current_config}")
    print()
    
    print("┌─────────────────────────────────────────────────────────────────┐")
    print("│                 STARTUP OPTIONS                          │")
    print("├─────────────────────────────────────────────────────────────────┤")
    print("│ 1️⃣ 🟢 Enable Live on Boot    4️⃣ 🔙 Back to Main       │")
    print("│ 2️⃣ 🔴 Disable Live on Boot  5️⃣ ⚙️ Custom Command      │")
    print("│ 3️⃣ 📊 Show Status                                          │")
    print("└─────────────────────────────────────────────────────────────────┘")
    
    try:
        choice = input("⚡ Select option: ").strip()
        
        if choice == '1':
            enable_live_startup()
        elif choice == '2':
            disable_live_startup()
        elif choice == '3':
            show_startup_status()
        elif choice == '4':
            return  # Use return instead of return
        elif choice == '5':
            set_custom_startup()
        else:
            print("\n❌ Invalid option!")
            
        input("\n⏸️  Press Enter to continue...")
        
    except KeyboardInterrupt:
        return
    except Exception as e:
        print(f"❌ Error: {e}")
        input("\n⏸️  Press Enter to continue...")

def enable_live_startup():
    """Enable live monitoring on boot"""
    try:
        service_content = f"""[Unit]
Description=ABYSSAL Live Monitoring
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 {os.path.abspath(__file__)} --live
Restart=always
User=root
Group=root

[Install]
WantedBy=multi-user.target
"""
        
        service_file = "/etc/systemd/system/abyssal-live.service"
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
        subprocess.run(['sudo', 'systemctl', 'enable', 'abyssal-live.service'], check=True)
        
        with open(f"{CONFIG_DIR}/startup-config", 'w') as f:
            f.write("live-monitoring-enabled")
        
        print("✅ Live monitoring enabled on boot")
        
    except Exception as e:
        print(f"❌ Failed to enable startup: {e}")

def disable_live_startup():
    """Disable live monitoring on boot"""
    try:
        subprocess.run(['sudo', 'systemctl', 'disable', 'abyssal-live.service'], check=True)
        subprocess.run(['sudo', 'systemctl', 'stop', 'abyssal-live.service'], check=True)
        
        with open(f"{CONFIG_DIR}/startup-config", 'w') as f:
            f.write("live-monitoring-disabled")
        
        print("🔴 Live monitoring disabled on boot")
        
    except Exception as e:
        print(f"❌ Failed to disable startup: {e}")

def show_startup_status():
    """Show current startup status"""
    try:
        result = subprocess.run(['sudo', 'systemctl', 'is-enabled', 'abyssal-live.service'], 
                              capture_output=True, text=True)
        
        if 'enabled' in result.stdout:
            print("🟢 Live monitoring is ENABLED on boot")
        elif 'disabled' in result.stdout:
            print("🔴 Live monitoring is DISABLED on boot")
        else:
            print("❓ Live monitoring status unknown")
            
    except Exception as e:
        print(f"❌ Failed to check status: {e}")

def set_custom_startup():
    """Set custom startup command"""
    try:
        cmd = input("Enter custom startup command: ").strip()
        
        if cmd:
            service_content = f"""[Unit]
Description=ABYSSAL Custom Startup
After=network.target

[Service]
Type=simple
ExecStart=/bin/bash -c "{cmd}"
Restart=always
User=root
Group=root

[Install]
WantedBy=multi-user.target
"""
            
            service_file = "/etc/systemd/system/abyssal-custom.service"
            with open(service_file, 'w') as f:
                f.write(service_content)
            
            subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
            subprocess.run(['sudo', 'systemctl', 'enable', 'abyssal-custom.service'], check=True)
            
            with open(f"{CONFIG_DIR}/startup-config", 'w') as f:
                f.write(f"custom: {cmd}")
            
            print(f"✅ Custom startup command set: {cmd}")
        else:
            print("❌ No command provided")
            
    except Exception as e:
        print(f"❌ Failed to set custom startup: {e}")

def start_live_monitoring():
    """Start live monitoring with alerts"""
    clear_screen()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                   LIVE MONITORING                        ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    print("🔊 ALARM SYSTEM ACTIVE - Real-time threat detection")
    print("🔄 Scanning every 30 seconds - Press Ctrl+C to stop")
    print()
    
    alert_count = 0
    
    try:
        while True:
            timestamp = time.strftime('%H:%M:%S')
            print(f"🕐 {timestamp} - Scanning system...")
            
            # Quick threat detection
            threats = quick_threat_scan()
            
            if threats:
                alert_count += 1
                print(f"\n🚨🚨🚨 THREAT DETECTED! 🚨🚨🚨")
                print(f"🔊 ALARM ACTIVATED! 🔊")
                print(f"⚠️  {len(threats)} threat(s) found:")
                
                # Play alarm
                play_alarm()
                
                # Show threats
                for threat in threats[:3]:
                    print(f"   {threat}")
                
                if len(threats) > 3:
                    print(f"   ... and {len(threats) - 3} more threats")
                
                print(f"📊 Total alerts: {alert_count}")
                print("━" * 60)
            else:
                print("✅ System secure - No threats detected")
            
            time.sleep(30)
            
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Live monitoring stopped")
        print(f"📊 Total threat alerts: {alert_count}")
    except Exception as e:
        print(f"\n❌ Monitoring error: {e}")

def quick_threat_scan():
    """Quick threat detection scan"""
    threats_found = []
    
    # Scan common locations
    locations = ['/tmp', '/var/tmp', os.path.expanduser('~/.cache'), os.path.expanduser('~/.local/share')]
    
    for location in locations:
        try:
            for root, dirs, files in os.walk(location):
                for file in files:
                    path = os.path.join(root, file)
                    
                    # Check for suspicious files
                    if any(keyword in file.lower() for keyword in ['malware', 'virus', 'backdoor', 'rootkit']):
                        threats_found.append(f"[THREAT] Suspicious file: {path}")
                    
                    # Check for hidden executables
                    if file.startswith('.') and os.access(path, os.X_OK):
                        threats_found.append(f"[THREAT] Hidden executable: {path}")
                    
                    if len(threats_found) > 10:
                        return
                if len(threats_found) > 10:
                    return
        except:
            continue
    
    # Check processes
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=5)
        for line in result.stdout.split('\n'):
            if any(keyword in line.lower() for keyword in ['nc -l', 'netcat', 'reverse', 'backdoor']):
                parts = line.split()
                if len(parts) > 10:
                    pid = parts[1]
                    cmd = ' '.join(parts[10:])
                    threats_found.append(f"[THREAT] Suspicious process PID {pid}: {cmd}")
    except:
        pass
    
    return threats_found

def play_alarm():
    """Play alarm sound"""
    try:
        # Try different alarm methods
        methods = [
            lambda: subprocess.run(['echo', '\a'], check=True),
            lambda: subprocess.run(['paplay', '/usr/share/sounds/alsa/Front_Left.wav'], check=True, capture_output=True),
            lambda: subprocess.run(['beep', '-f', '1000', '-l', '500'], check=True, capture_output=True)
        ]
        
        for method in methods:
            try:
                method()
                return
            except:
                continue
    except:
        print('\a', end='', flush=True)

def interactive_mode():
    """Main interactive mode"""
    main_menu()

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
    print("  python3 abyssal.py --control      # Control all features on/off")
    print("  python3 abyssal.py --harden       # System hardening")
    print("  python3 abyssal.py --full         # Run all modules")
    print("  python3 abyssal.py --logkiller    # Erase system logs")
    print("  python3 abyssal.py --antimitm     # Run anti-MITM checks")
    print("  python3 abyssal.py --anon         # Start anonymity mode\n")
    print("Run with sudo if required for system-level actions.\n")

def full_mode():
    log_info("Running full mode: anonymity, scan, hardening.")
    anon_mode()
    scan_mode()
    harden_mode()

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
    parser.add_argument('--control', action='store_true', help='Control all features on/off')
    parser.add_argument('--harden', action='store_true', help='System hardening')
    parser.add_argument('--full', action='store_true', help='Run all modules')
    parser.add_argument('--logkiller', action='store_true', help='Erase system logs')
    parser.add_argument('--antimitm', action='store_true', help='Run anti-MITM checks')
    args = parser.parse_args()

    if args.control:
        feature_menu()
    elif args.anon:
        if get_feature_state('anon') == 'on':
            anon_mode()
        else:
            print("❌ ANON feature is disabled. Use --control to enable it.")
    elif args.scan:
        if get_feature_state('scan') == 'on':
            scan_mode()
        else:
            print("❌ SCAN feature is disabled. Use --control to enable it.")
    elif args.fix:
        if get_feature_state('fix') == 'on':
            run_with_sudo(fix_mode, 'fix_mode')
        else:
            print("❌ FIX feature is disabled. Use --control to enable it.")
    elif args.interactive:
        if get_feature_state('interactive') == 'on':
            interactive_mode()
        else:
            print("❌ INTERACTIVE feature is disabled. Use --control to enable it.")
    elif args.live:
        if get_feature_state('live') == 'on':
            start_live_monitoring()
        else:
            print("❌ LIVE feature is disabled. Use --control to enable it.")
    elif args.live_on:
        enable_live_startup()
    elif args.live_off:
        disable_live_startup()
    elif args.startup:
        startup_menu()
    elif args.harden:
        if get_feature_state('harden') == 'on':
            run_with_sudo(harden_mode, 'harden_mode')
        else:
            print("❌ HARDEN feature is disabled. Use --control to enable it.")
    elif args.full:
        if get_feature_state('full') == 'on':
            full_mode()
        else:
            print("❌ FULL feature is disabled. Use --control to enable it.")
    elif args.logkiller:
        if get_feature_state('logkiller') == 'on':
            run_with_sudo(logkiller_mode, 'logkiller_mode')
        else:
            print("❌ LOGKILLER feature is disabled. Use --control to enable it.")
    elif args.antimitm:
        if get_feature_state('antimitm') == 'on':
            run_with_sudo(antimitm_mode, 'antimitm_mode')
        else:
            print("❌ ANTIMITM feature is disabled. Use --control to enable it.")
    else:
        pass

if __name__ == "__main__":
    main()
