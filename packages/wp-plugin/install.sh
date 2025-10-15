#!/bin/bash
#
# AIIndex WordPress Plugin Installation Script
#
# Usage: ./install.sh /path/to/wordpress
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if WordPress path is provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: WordPress path not provided${NC}"
    echo "Usage: $0 /path/to/wordpress"
    exit 1
fi

WP_PATH="$1"
PLUGIN_NAME="aiindex"
CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Verify WordPress installation
if [ ! -f "$WP_PATH/wp-config.php" ]; then
    echo -e "${RED}Error: WordPress installation not found at $WP_PATH${NC}"
    exit 1
fi

PLUGINS_DIR="$WP_PATH/wp-content/plugins"
PLUGIN_DIR="$PLUGINS_DIR/$PLUGIN_NAME"

echo -e "${GREEN}AIIndex WordPress Plugin Installer${NC}"
echo "=================================="
echo ""
echo "WordPress path: $WP_PATH"
echo "Plugin directory: $PLUGIN_DIR"
echo ""

# Check if plugin already exists
if [ -d "$PLUGIN_DIR" ]; then
    echo -e "${YELLOW}Warning: Plugin directory already exists${NC}"
    read -p "Do you want to overwrite it? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
    rm -rf "$PLUGIN_DIR"
fi

# Create plugin directory
echo "Creating plugin directory..."
mkdir -p "$PLUGIN_DIR"

# Copy files
echo "Copying plugin files..."
cp -r "$CURRENT_DIR"/* "$PLUGIN_DIR/"

# Remove installation script from plugin directory
rm -f "$PLUGIN_DIR/install.sh"

# Set permissions
echo "Setting permissions..."
chmod 755 "$PLUGIN_DIR"
find "$PLUGIN_DIR" -type f -exec chmod 644 {} \;
find "$PLUGIN_DIR" -type d -exec chmod 755 {} \;

echo ""
echo -e "${GREEN}✓ Installation complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Log in to your WordPress admin panel"
echo "2. Navigate to Plugins > Installed Plugins"
echo "3. Find 'AIIndex for WordPress' and click Activate"
echo "4. Go to AIIndex > Settings to configure"
echo ""
echo "Documentation: $PLUGIN_DIR/README.md"
echo "Installation guide: $PLUGIN_DIR/INSTALL.md"
echo ""
