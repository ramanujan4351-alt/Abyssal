Abyssal
Abyssal is a modular cybersecurity toolkit for Linux that helps you enhance privacy, scan for threats, harden your system, erase logs, and check for MITM attacks—all from a simple command-line interface.

Features
Anonymity mode
Custom antivirus scan
System hardening
Log eraser
Anti-MITM checks
Run all modules at once
Installation
Download or clone this repository.
Run scripts/install.sh to install dependencies.
Usage
Run python3 abyssal.py with any of these options:

--anon    Start anonymity mode
--scan    Run custom antivirus scan
--harden   System hardening
--full    Run all modules
--logkiller  Erase system logs
--antimitm  Run anti-MITM checks
Example:

python3 abyssal.py --full
Abyssal is ideal for security enthusiasts and advanced users who want a flexible, scriptable security toolkit for Linux systems.
