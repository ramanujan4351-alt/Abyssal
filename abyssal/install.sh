#!/bin/bash

# ABYSSAL SECURITY - AUTOMATIC INSTALLATION SCRIPT
# Installs all dependencies for AI/ML penetration testing framework

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          ABYSSAL SECURITY - AUTO INSTALLER                   ║"
echo "║        AI/ML Penetration Testing Framework                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo

echo "🔧 Installing ABYSSAL SECURITY dependencies..."
echo

# Update package list
echo "📦 Updating package lists..."
sudo apt update

# Install Python packages
echo "🐍 Installing Python packages..."
sudo apt install -y python3 python3-pip python3-dev

# Install ML/AI dependencies
echo "🧠 Installing Machine Learning dependencies..."
sudo apt install -y python3-sklearn python3-numpy python3-pandas python3-psutil

# Install additional security tools
echo "🔒 Installing security tools..."
sudo apt install -y nmap smbclient curl wget ftp

# Install additional Python packages if needed
echo "📦 Installing additional Python packages..."
sudo pip install --break-system-packages scikit-learn numpy pandas psutil

# Create config directories
echo "📁 Creating configuration directories..."
mkdir -p ~/.config/abyssal/models
mkdir -p ~/.config/abyssal/logs

# Set permissions
echo "🔐 Setting permissions..."
chmod +x abyssal.py

# Test installation
echo "🧪 Testing installation..."
python3 -c "
import sklearn, numpy, pandas, psutil
print('✅ All dependencies installed successfully!')
print(f'🤖 scikit-learn version: {sklearn.__version__}')
print(f'📊 numpy version: {numpy.__version__}')
print(f'🐼 pandas version: {pandas.__version__}')
print(f'⚡ psutil version: {psutil.__version__}')
" 2>/dev/null || {
    echo "❌ Installation failed - trying alternative method..."
    sudo pip3 install --break-system-packages scikit-learn numpy pandas psutil
}

echo
echo "✅ ABYSSAL SECURITY installation complete!"
echo
echo "🚀 QUICK START:"
echo "   python3 abyssal.py --interactive"
echo
echo "🤖 AI/ML COMMANDS:"
echo "   python3 abyssal.py --ml-monitor     # Real-time ML monitoring"
echo "   python3 abyssal.py --ml-scan        # ML comprehensive scan"
echo "   python3 abyssal.py --retrain        # Retrain ML models"
echo "   python3 abyssal.py --config         # Configure ML settings"

echo
echo "👤 ANONYMITY MODE:"
echo "   python3 abyssal.py --anon           # Activate anonymity mode"
echo "   python3 abyssal.py --check-anon     # Check anonymity status"
echo "   python3 abyssal.py --restore        # Restore original identity"

echo
echo "🔥 ALL AVAILABLE COMMANDS:"
echo "   --interactive      # Full AI/ML control panel"
echo "   --ml-monitor       # Real-time ML threat detection"
echo "   --ml-scan          # ML comprehensive security scan"
echo "   --anon            # Activate anonymity mode"
echo "   --check-anon      # Check anonymity status"
echo "   --restore         # Restore original identity"
echo "   --retrain          # Retrain ML models"
echo "   --config           # Configure ML settings"

echo
echo "🎮 INTERACTIVE MODE OPTIONS:"
echo "   1️⃣ 🤖 ML Real-time Monitor    # AI-powered real-time monitoring"
echo "   2️⃣ 🧠 ML Comprehensive Scan  # Full ML security analysis"
echo "   3️⃣ 📁 ML File Analysis      # ML file anomaly detection"
echo "   4️⃣ 🔧 ML Process Analysis   # ML process behavior analysis"
echo "   5️⃣ 🌐 ML Network Analysis  # ML network anomaly detection"
echo "   6️⃣ 👤 Anonymity Mode        # Complete identity protection"
echo "   7️⃣ 🔧 Retrain Models       # Retrain ML models"
echo "   8️⃣ ⚙️ ML Configuration      # Configure ML settings"
echo "   9️⃣ 📊 Model Statistics     # Show ML model info"
echo
echo "🔥 PERFECT FOR PENTESTERS - STAY ANONYMOUS, STAY SECURE! 🔥"
