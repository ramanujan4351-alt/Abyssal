#!/bin/bash

# Fix launcher permissions and trust settings

echo "🔧 Fixing Abyssal Security launchers..."

# Get the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Desktop and applications directories
DESKTOP_DIR="$HOME/Desktop"
APPLICATIONS_DIR="$HOME/.local/share/applications"

# Make launchers executable
echo "📝 Setting executable permissions..."
chmod +x "$SCRIPT_DIR/abyssal.py"
chmod +x "$SCRIPT_DIR/abyssal-launcher.sh"
chmod +x "$DESKTOP_DIR/Abyssal Security.desktop"
chmod +x "$DESKTOP_DIR/Abyssal Launcher.desktop"
chmod +x "$APPLICATIONS_DIR/abyssal.desktop"
chmod +x "$APPLICATIONS_DIR/Abyssal Launcher.desktop"

# Remove the "executable=false" flag from desktop files
echo "🔓 Removing execution restrictions..."
for desktop_file in "$DESKTOP_DIR"/*.desktop "$APPLICATIONS_DIR"/*.desktop; do
    if [ -f "$desktop_file" ]; then
        # Remove any executable=false line
        sed -i '/^Executable=/d' "$desktop_file" 2>/dev/null || true
        # Ensure Exec line points to correct path
        sed -i "s|Exec=.*abyssal.py|Exec=$SCRIPT_DIR/abyssal.py|g" "$desktop_file" 2>/dev/null || true
        sed -i "s|Exec=.*abyssal-launcher.sh|Exec=$SCRIPT_DIR/abyssal-launcher.sh|g" "$desktop_file" 2>/dev/null || true
    fi
done

# Update desktop database
echo "🗄️ Updating desktop database..."
update-desktop-database "$APPLICATIONS_DIR" 2>/dev/null || true

echo "✅ Launchers fixed! Try double-clicking them now."
echo
echo "🚀 You can also run directly from terminal:"
echo "   • $SCRIPT_DIR/abyssal-launcher.sh (interactive menu)"
echo "   • python3 $SCRIPT_DIR/abyssal.py --interactive"
echo
echo "💡 If double-clicking still shows 'allow launching', right-click → Properties → Permissions → Allow executing"
