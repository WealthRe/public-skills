#!/bin/bash

# OpenClaw Installer Script
# This script automates the installation and configuration of OpenClaw on Linux systems.

set -e

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to get system architecture
get_arch() {
    uname -m
}

# Function to get OS information
get_os_info() {
    if [ -f /etc/os-release ]; then
        # Read /etc/os-release for OS information
        . /etc/os-release
        OS_NAME=$NAME
        OS_VERSION=$VERSION_ID
    elif [ -f /etc/redhat-release ]; then
        # For older RedHat/CentOS systems
        OS_NAME=$(cat /etc/redhat-release | cut -d' ' -f1)
        OS_VERSION=$(cat /etc/redhat-release | grep -oE '[0-9]+\.[0-9]+')
    else
        OS_NAME=$(uname -s)
        OS_VERSION=$(uname -r)
    fi

    # Normalize OS name
    if echo "$OS_NAME" | grep -qi "ubuntu"; then
        OS_NAME="ubuntu"
    elif echo "$OS_NAME" | grep -qi "debian"; then
        OS_NAME="debian"
    elif echo "$OS_NAME" | grep -qi "centos\|rhel\|redhat"; then
        OS_NAME="centos"
    elif echo "$OS_NAME" | grep -qi "fedora"; then
        OS_NAME="fedora"
    elif echo "$OS_NAME" | grep -qi "openEuler"; then
        OS_NAME="openeuler"
    elif echo "$OS_NAME" | grep -qi "kylin"; then
        # Kylin Linux (which is based on CentOS/RHEL)
        OS_NAME="centos"
    else
        OS_NAME=$(uname -s)
    fi

    echo "$OS_NAME $OS_VERSION"
}

# Function to install dependencies based on OS
install_dependencies() {
    local os=$1
    local arch=$(get_arch)

    echo "Installing dependencies for $os..."

    case $os in
        ubuntu|debian)
            # Debian/Ubuntu
            if ! command_exists apt-get; then
                echo "apt-get is not available. Please check your system."
                exit 1
            fi

            # Skip apt-get update to save time and space
            apt-get install -y git cmake gcc g++ make
            ;;
        centos|rhel|redhat)
            # CentOS/RHEL
            if ! command_exists yum; then
                echo "yum is not available. Please check your system."
                exit 1
            fi

            # Skip yum update to save time and space
            yum install -y git cmake gcc gcc-c++ make
            ;;
        fedora)
            # Fedora
            if ! command_exists dnf; then
                echo "dnf is not available. Please check your system."
                exit 1
            fi

            # Skip dnf update to save time and space
            dnf install -y git cmake gcc gcc-c++ make
            ;;
        openeuler)
            # openEuler
            if ! command_exists yum; then
                echo "yum is not available. Please check your system."
                exit 1
            fi

            # Skip yum update to save time and space
            yum install -y git cmake gcc gcc-c++ make
            ;;
        *)
            echo "Unsupported OS: $os"
            exit 1
            ;;
    esac

    echo "Dependencies installed successfully."
}

# Function to install Node.js
install_nodejs() {
    local arch=$(get_arch)
    local node_version="v22.12.0"
    local node_dir="/usr/local/nodejs"

    echo "Installing Node.js $node_version..."

    # Create installation directory
    mkdir -p $node_dir

    # Download Node.js
    case $arch in
        x86_64)
            node_tarball="node-${node_version}-linux-x64.tar.xz"
            ;;
        aarch64|arm64)
            node_tarball="node-${node_version}-linux-arm64.tar.xz"
            ;;
        *)
            echo "Unsupported architecture: $arch"
            exit 1
            ;;
    esac

    node_url="https://nodejs.org/dist/${node_version}/${node_tarball}"
    echo "Downloading Node.js from: $node_url"

    if ! wget -q $node_url -P $node_dir; then
        echo "Failed to download Node.js. Please check your internet connection."
        exit 1
    fi

    # Extract Node.js
    cd $node_dir
    tar -xJf $node_tarball
    rm -f $node_tarball

    # Create symbolic links
    ln -sf $node_dir/node-${node_version}-linux-$(uname -m)/bin/node /usr/bin/node
    ln -sf $node_dir/node-${node_version}-linux-$(uname -m)/bin/npm /usr/bin/npm

    # Verify Node.js installation
    node_version=$(node -v)
    npm_version=$(npm -v)
    echo "Node.js $node_version installed successfully"
    echo "npm $npm_version installed successfully"
}

# Function to install OpenClaw
install_openclaw() {
    echo "Installing OpenClaw..."

    # Set npm to use official registry
    npm config set registry https://registry.npmjs.org

    # Install OpenClaw globally
    if ! npm install -g openclaw --verbose; then
        echo "Failed to install OpenClaw. Please check your internet connection and try again."
        exit 1
    fi

    # Create symbolic link if not exists
    if [ ! -e /usr/bin/openclaw ]; then
        local node_dir=$(npm prefix -g)/bin
        ln -sf $node_dir/openclaw /usr/bin/openclaw
    fi

    echo "OpenClaw installed successfully"
}

# Function to create systemd service
create_systemd_service() {
    local service_file="/etc/systemd/system/openclaw-gateway.service"

    echo "Creating systemd service file at $service_file..."

    # Create systemd service file
    cat > $service_file <<'EOF'
[Unit]
Description=OpenClaw Gateway Service
After=network.target network-online.target

[Service]
Type=simple
User=root
ExecStart=/usr/bin/openclaw gateway run --port 18789 --bind loopback --allow-unconfigured --force
Restart=always
RestartSec=5
Environment=PATH=/usr/local/nodejs/node-v22.12.0-linux-arm64/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin
StandardOutput=journal+console
StandardError=journal+console

[Install]
WantedBy=multi-user.target
EOF

    # Fix the PATH in the service file based on actual Node.js installation
    local node_dir=$(npm prefix -g)
    local node_bindir=$(readlink -f /usr/bin/node | sed -E 's|/bin/node$||')
    sed -i "s|/usr/local/nodejs/node-v22.12.0-linux-arm64/bin|${node_bindir}|g" $service_file

    # Reload systemd and enable the service
    systemctl daemon-reload
    systemctl enable --now openclaw-gateway

    echo "Systemd service created and enabled successfully"
}

# Function to configure feishu channel
configure_feishu_channel() {
    echo "=== Feishu Channel Configuration ==="
    read -p "Do you want to configure Feishu channel? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping Feishu channel configuration"
        return
    fi

    read -p "Enter Feishu App ID: " FEISHU_APP_ID
    read -p "Enter Feishu App Secret: " FEISHU_APP_SECRET

    # Create OpenClaw config directory if not exists
    mkdir -p ~/.openclaw

    # Copy template to config file
    cp ./assets/openclaw.json.template ~/.openclaw/openclaw.json

    # Replace placeholders in config file
    sed -i "s/{{feishu_app_id}}/$FEISHU_APP_ID/g" ~/.openclaw/openclaw.json
    sed -i "s/{{feishu_app_secret}}/$FEISHU_APP_SECRET/g" ~/.openclaw/openclaw.json
    sed -i "s/{{feishu_enabled}}/true/g" ~/.openclaw/openclaw.json
    sed -i "s/{{discord_enabled}}/false/g" ~/.openclaw/openclaw.json

    echo "Feishu channel configuration completed"
}

# Function to configure Aliyun model
configure_aliyun_model() {
    echo "=== Aliyun Model Configuration ==="
    read -p "Do you want to configure Aliyun model? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping Aliyun model configuration"
        return
    fi

    read -p "Enter Aliyun API Key: " ALIYUN_API_KEY
    read -p "Enter Aliyun Base URL (default: https://dashscope.aliyuncs.com/compatible-mode/v1): " ALIYUN_BASE_URL
    ALIYUN_BASE_URL=${ALIYUN_BASE_URL:-https://dashscope.aliyuncs.com/compatible-mode/v1}

    # Create OpenClaw config directory if not exists
    mkdir -p ~/.openclaw

    # Copy template to config file if not exists
    if [ ! -f ~/.openclaw/openclaw.json ]; then
        cp ./assets/openclaw.json.template ~/.openclaw/openclaw.json
    fi

    # Replace placeholders in config file
    sed -i "s/{{aliyun_api_key}}/$ALIYUN_API_KEY/g" ~/.openclaw/openclaw.json
    sed -i "s/{{aliyun_base_url}}/$ALIYUN_BASE_URL/g" ~/.openclaw/openclaw.json

    echo "Aliyun model configuration completed"
}

# Function to set current timestamp
set_timestamp() {
    TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")
    if [ -f ~/.openclaw/openclaw.json ]; then
        sed -i "s/{{timestamp}}/$TIMESTAMP/g" ~/.openclaw/openclaw.json
    fi
}

# Function to verify installation
verify_installation() {
    echo "Verifying installation..."

    # Check if OpenClaw command exists
    if ! command_exists openclaw; then
        echo "OpenClaw command not found"
        return 1
    fi

    # Check gateway status
    if ! systemctl is-active openclaw-gateway >/dev/null 2>&1; then
        echo "OpenClaw gateway service is not active"
        return 1
    fi

    # Check gateway health
    if ! openclaw gateway health >/dev/null 2>&1; then
        echo "OpenClaw gateway health check failed"
        return 1
    fi

    echo "Installation verified successfully"
    return 0
}

# Main function
main() {
    echo "=== OpenClaw Installer ==="
    echo

    # Check if running as root
    if [ "$EUID" -ne 0 ]; then
        echo "Please run as root"
        exit 1
    fi

    # Get system information
    echo "Checking system information..."
    os_info=$(get_os_info)
    arch=$(get_arch)
    echo "OS: $os_info"
    echo "Architecture: $arch"
    echo

    # Install dependencies
    install_dependencies $(echo $os_info | cut -d' ' -f1)
    echo

    # Install Node.js
    install_nodejs
    echo

    # Install OpenClaw
    install_openclaw
    echo

    # Configure Feishu channel
    configure_feishu_channel
    echo

    # Configure Aliyun model
    configure_aliyun_model
    echo

    # Set current timestamp
    set_timestamp
    echo

    # Create systemd service
    create_systemd_service
    echo

    # Verify installation
    if verify_installation; then
        echo
        echo "OpenClaw installation completed successfully!"
    else
        echo
        echo "OpenClaw installation failed!"
        exit 1
    fi
}

# Run main function
main "$@"