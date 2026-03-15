#!/bin/bash

# ABYSSAL SECURITY LAUNCHER
# Interactive launcher for Abyssal Security Framework

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Clear screen
clear

# Banner
echo -e "${RED}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${RED}║          ABYSSAL SECURITY - AI/ML FRAMEWORK                   ║${NC}"
echo -e "${RED}║        Advanced Threat Detection & Anonymity System          ║${NC}"
echo -e "${RED}╚══════════════════════════════════════════════════════════════╝${NC}"
echo

# Menu
echo -e "${CYAN}🚀 LAUNCH OPTIONS:${NC}"
echo
echo -e "${GREEN}1️⃣  🤖 Interactive AI/ML Control Panel${NC}"
echo -e "${GREEN}2️⃣  🔍 ML Real-time Monitoring${NC}"
echo -e "${GREEN}3️⃣  🧠 ML Comprehensive Scan${NC}"
echo -e "${GREEN}4️⃣  👤 Activate Anonymity Mode${NC}"
echo -e "${GREEN}5️⃣  🔍 Check Anonymity Status${NC}"
echo -e "${GREEN}6️⃣  🔄 Restore Identity${NC}"
echo -e "${GREEN}7️⃣  🔧 Retrain ML Models${NC}"
echo -e "${GREEN}8️⃣  ⚙️ ML Configuration${NC}"
echo -e "${GREEN}9️⃣  📊 Model Statistics${NC}"
echo -e "${GREEN}🔟  ❌ Exit${NC}"
echo

echo -e "${YELLOW}💡 QUICK COMMANDS:${NC}"
echo -e "${YELLOW}   --ml-monitor     # Real-time ML monitoring${NC}"
echo -e "${YELLOW}   --ml-scan        # ML comprehensive scan${NC}"
echo -e "${YELLOW}   --anon           # Activate anonymity mode${NC}"
echo -e "${YELLOW}   --check-anon     # Check anonymity status${NC}"
echo

# Get user choice
echo -n -e "${PURPLE}⚡ Select option (1-10): ${NC}"
read choice

case $choice in
    1)
        echo -e "${BLUE}🚀 Starting Interactive AI/ML Control Panel...${NC}"
        python3 "$SCRIPT_DIR/abyssal.py" --interactive
        ;;
    2)
        echo -e "${BLUE}🔍 Starting ML Real-time Monitoring...${NC}"
        echo -e "${YELLOW}⚠️  Press Ctrl+C to stop monitoring${NC}"
        python3 "$SCRIPT_DIR/abyssal.py" --ml-monitor
        ;;
    3)
        echo -e "${BLUE}🧠 Running ML Comprehensive Scan...${NC}"
        python3 "$SCRIPT_DIR/abyssal.py" --ml-scan
        ;;
    4)
        echo -e "${BLUE}👤 Activating Anonymity Mode...${NC}"
        echo -e "${YELLOW}⚠️  This requires sudo privileges${NC}"
        python3 "$SCRIPT_DIR/abyssal.py" --anon
        ;;
    5)
        echo -e "${BLUE}🔍 Checking Anonymity Status...${NC}"
        python3 "$SCRIPT_DIR/abyssal.py" --check-anon
        ;;
    6)
        echo -e "${BLUE}🔄 Restoring Original Identity...${NC}"
        echo -e "${YELLOW}⚠️  This requires sudo privileges${NC}"
        python3 "$SCRIPT_DIR/abyssal.py" --restore
        ;;
    7)
        echo -e "${BLUE}🔧 Retraining ML Models...${NC}"
        echo -e "${YELLOW}⚠️  This may take a few minutes${NC}"
        python3 "$SCRIPT_DIR/abyssal.py" --retrain
        ;;
    8)
        echo -e "${BLUE}⚙️ Opening ML Configuration...${NC}"
        python3 "$SCRIPT_DIR/abyssal.py" --config
        ;;
    9)
        echo -e "${BLUE}📊 Showing Model Statistics...${NC}"
        python3 "$SCRIPT_DIR/abyssal.py" --interactive
        # Auto-select option 9 for model statistics
        echo "9" | python3 "$SCRIPT_DIR/abyssal.py" --interactive
        ;;
    10)
        echo -e "${GREEN}👋 Goodbye! Stay safe!${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}❌ Invalid option! Please select 1-10${NC}"
        echo -e "${YELLOW}Press Enter to try again...${NC}"
        read
        exec "$0"  # Restart the launcher
        ;;
esac

echo
echo -e "${GREEN}✅ Operation completed!${NC}"
echo -e "${YELLOW}Press Enter to return to launcher...${NC}"
read
exec "$0"  # Restart the launcher
