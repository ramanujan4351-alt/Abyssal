# Abyssal

Abyssal is a modular cybersecurity toolkit for Linux that helps you enhance privacy, scan for threats, harden your system, erase logs, and check for MITM attacks—all from a simple command-line interface.

## 🚀 INSTALLATION
 
## **Step 1: Clone the Repository**
```bash
`git clone https://github.com/yourusername/abyssal.git`
`cd abyssal`
Step 2: Run the Auto-Installer
`bash`
chmod +x install.sh
./install.sh
What the installer does:

✅ Updates package lists
✅ Installs Python3 and pip
✅ Installs ML packages: scikit-learn, numpy, pandas, psutil
✅ Installs security tools: nmap, smbclient, curl, ftp
✅ Creates configuration directories
✅ Sets permissions and tests installation
Step 3: Verify Installation
bash
python3 abyssal.py --help
🔧 QUICK START
For Immediate Protection:
bash
# Start AI/ML real-time monitoring
python3 abyssal.py --ml-monitor
 
# Activate complete anonymity
python3 abyssal.py --anon
 
# Run comprehensive security scan
python3 abyssal.py --ml-scan
For Interactive Control:
bash
python3 abyssal.py --interactive (not functional currently)
🤖 AI/ML FEATURES
🧠 Machine Learning Models:
Isolation Forest - Unsupervised anomaly detection
One-Class SVM - Novelty detection for outliers
Random Forest - Supervised classification
Feature Scaling - StandardScaler for normalization
📊 Advanced Feature Extraction:
400+ features per data point
Shannon entropy analysis for encrypted content
Byte frequency distribution
Process behavior patterns
Network connection analysis
File metadata examination
🔍 Real-time Threat Detection:
bash
# Continuous ML monitoring (15-second intervals)
python3 abyssal.py --ml-monitor
 
# One-time comprehensive scan
python3 abyssal.py --ml-scan
 
# Analyze specific file
python3 abyssal.py --interactive
# Select option 3: ML File Analysis
👤 ANONYMITY MODE
🎭 Complete Identity Protection:
bash
# Activate full anonymity
python3 abyssal.py --anon
What it does:

🌐 Tor Service - Routes all traffic through Tor
🔧 MAC Randomization - Generates random MAC addresses
🏷️ Hostname Change - Sets random hostname
🗑️ DNS Cache Flush - Clears DNS history
🔑 Process Killer - Terminates keyring/secret services
🌐 Proxy Setup - Configures HTTP/HTTPS/SOCKS proxies
🔍 Status Monitoring:
bash
# Check anonymity status
python3 abyssal.py --check-anon
Shows:

Tor service status
Current MAC addresses
Current hostname
Proxy environment variables
Dangerous processes detection
🔄 Safe Restoration:
bash
# Restore original identity
python3 abyssal.py --restore
📚 COMMAND REFERENCE
🤖 AI/ML Commands:
bash
python3 abyssal.py --interactive    # Full AI/ML control panel
python3 abyssal.py --ml-monitor     # Real-time ML monitoring
python3 abyssal.py --ml-scan        # ML comprehensive scan
python3 abyssal.py --retrain        # Retrain ML models
python3 abyssal.py --config         # Configure ML settings
👤 Anonymity Commands:
bash
python3 abyssal.py --anon           # Activate anonymity mode
python3 abyssal.py --check-anon     # Check anonymity status
python3 abyssal.py --restore        # Restore original identity
🎮 Interactive Mode Options:
1️⃣ 🤖 ML Real-time Monitor    # AI-powered real-time monitoring
2️⃣ 🧠 ML Comprehensive Scan  # Full ML security analysis
3️⃣ 📁 ML File Analysis      # ML file anomaly detection
4️⃣ 🔧 ML Process Analysis   # ML process behavior analysis
5️⃣ 🌐 ML Network Analysis  # ML network anomaly detection
6️⃣ 👤 Anonymity Mode        # Complete identity protection
7️⃣ 🔧 Retrain Models       # Retrain ML models
8️⃣ ⚙️ ML Configuration      # Configure ML settings
9️⃣ 📊 Model Statistics     # Show ML model info
🎯 USE CASES
🔒 For Pentesters:
bash
# Before pentesting - go anonymous
python3 abyssal.py --anon
 
# During pentesting - monitor for threats
python3 abyssal.py --ml-monitor
 
# After pentesting - restore identity
python3 abyssal.py --restore
🛡️ For System Security:
bash
# Continuous monitoring
python3 abyssal.py --ml-monitor
 
# Periodic comprehensive scans
python3 abyssal.py --ml-scan
 
# Analyze suspicious files
python3 abyssal.py --interactive
# Option 3: ML File Analysis
🔍 For Incident Response:
bash
# Quick threat assessment
python3 abyssal.py --ml-scan
 
# Detailed process analysis
python3 abyssal.py --interactive
# Option 4: ML Process Analysis
 
# Network anomaly detection
python3 abyssal.py --interactive
# Option 5: ML Network Analysis
⚙️ CONFIGURATION
📁 Configuration Files:
bash
~/.config/abyssal/
├── models/           # Trained ML models
├── logs/            # Log files
└── config.json      # Configuration settings
🔧 Configure Settings:
bash
python3 abyssal.py --config
Available settings:

ml_detection: Toggle ML detection
scan_interval: Change scan frequency
auto_quarantine: Toggle automatic quarantine
alert_sound: Toggle alert sounds
🧠 Retrain Models:
bash
# Retrain with current system data
python3 abyssal.py --retrain
🐛 TROUBLESHOOTING
❌ Common Issues:
Installation Errors:
bash
# If pip fails, try system packages
sudo apt install python3-sklearn python3-numpy python3-pandas python3-psutil
 
# If permissions fail
sudo chmod +x abyssal.py install.sh
ML Model Errors:
bash
# Reset ML models
rm -rf ~/.config/abyssal/models/
python3 abyssal.py --retrain
Anonymity Mode Issues:
bash
# Check Tor status
sudo systemctl status tor
 
# Start Tor manually
sudo systemctl start tor
 
# Check MAC change permissions
sudo ifconfig
Permission Errors:
bash
# Fix permissions
sudo chown $USER:$USER ~/.config/abyssal/ -R
chmod +x abyssal.py
🔍 Debug Mode:
bash
# Enable debug logging
export PYTHONPATH=/path/to/abyssal
python3 abyssal.py --ml-monitor 2>&1 | tee abyssal.log
📊 PERFORMANCE
⚡ System Requirements:
CPU: 2+ cores recommended
RAM: 4GB+ recommended
Storage: 1GB+ for models
Network: Tor connection for anonymity
📈 ML Model Performance:
Training time: 2-5 minutes initial
Inference time: <1 second per scan
Memory usage: ~200MB for models
CPU usage: 10-20% during monitoring
🛡️ SECURITY NOTES
⚠️ Important Warnings:
Anonymity mode requires sudo privileges
Tor service must be installed and running
MAC changes may temporarily disconnect network
Process termination may affect some applications
🔐 Best Practices:
Always check anonymity status after activation
Restore identity when finished
Keep models updated with regular retraining
Monitor logs for false positives
Test in safe environment before critical use
📝 LICENSE
This project is licensed under the MIT License.

🤝 CONTRIBUTING
Fork the repository
Create your feature branch (git checkout -b feature/AmazingFeature)
Commit your changes (git commit -m 'Add some AmazingFeature')
Push to the branch (git push origin feature/AmazingFeature)
Open a Pull Request
📞 SUPPORT
🐛 Report bugs: Create an issue
💡 Feature requests: Create an issue with "enhancement" label
🔒 Security issues: Contact maintainers directly
🙏 ACKNOWLEDGMENTS
scikit-learn - Machine learning library
psutil - System monitoring
Tor Project - Anonymity network
🔥 READY FOR PENTESTERS - STAY ANONYMOUS, STAY SECURE! 🔥
Made with ❤️ for the cybersecurity community
# NOTE : EXPECT BUGS AND ISSUES AS THE TOOL IS STILL UNDER DEVELOPMENT
