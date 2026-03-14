import argparse
from modules.anon import anon_mode
from modules.scan import scan_mode
from modules.harden import harden_mode
from modules.logkiller import logkiller_mode
from modules.antimitm import antimitm_mode
from modules.logs import log_info

def full_mode():
    log_info("Running full mode: anonymity, scan, hardening.")
    anon_mode()
    scan_mode()
    harden_mode()

def print_logo_and_usage():
    print("\n┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
    print("┃      🕶️   ＡＢＹＳＳＡＬ   🐍      ┃")
    print("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n")
    print("Usage:")
    print("  python3 abyssal.py --help         # Show help")
    print("  python3 abyssal.py --anon         # Start anonymity mode")
    print("  python3 abyssal.py --scan         # Run custom antivirus scan")
    print("  python3 abyssal.py --harden       # System hardening")
    print("  python3 abyssal.py --full         # Run all modules")
    print("  python3 abyssal.py --logkiller    # Erase system logs")
    print("  python3 abyssal.py --antimitm     # Run anti-MITM checks\n")
    print("Run with sudo if required for system-level actions.\n")

def main():
    print_logo_and_usage()
    parser = argparse.ArgumentParser(description="Abyssal CLI: Born from the abyss, hunting malware in the shadows.")
    parser.add_argument('--anon', action='store_true', help='Start anonymity mode')
    parser.add_argument('--scan', action='store_true', help='Run custom antivirus scan')
    parser.add_argument('--harden', action='store_true', help='System hardening')
    parser.add_argument('--full', action='store_true', help='Run all modules')
    parser.add_argument('--logkiller', action='store_true', help='Erase system logs')
    parser.add_argument('--antimitm', action='store_true', help='Run anti-MITM checks')
    args = parser.parse_args()

    if args.anon:
        anon_mode()
    elif args.scan:
        scan_mode()
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
