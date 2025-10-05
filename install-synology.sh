#!/bin/bash

# UNS-ClaudeJP 1.0 - Installation Script for Synology NAS
# This script helps deploy the application on Synology NAS using Docker

set -e

echo "=========================================="
echo "UNS-ClaudeJP 1.0 - Installation Script"
echo "Sistema de Gestión de Personal Temporal"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if running on Synology
if [ ! -f /etc/synoinfo.conf ]; then
    echo -e "${YELLOW}Warning: This doesn't appear to be a Synology NAS${NC}"
    echo "Continue anyway? (y/n)"
    read -r response
    if [ "$response" != "y" ]; then
        exit 1
    fi
fi

# Check Docker installation
echo -e "${BLUE}Checking Docker installation...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed!${NC}"
    echo "Please install Docker from Synology Package Center first."
    exit 1
fi
echo -e "${GREEN}✓ Docker is installed${NC}"

# Check Docker Compose
echo -e "${BLUE}Checking Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Docker Compose not found, attempting to install...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi
echo -e "${GREEN}✓ Docker Compose is ready${NC}"

# Set installation directory
INSTALL_DIR="/volume1/docker/uns-claudejp"
echo ""
echo -e "${BLUE}Installation directory: ${INSTALL_DIR}${NC}"
echo "Change directory? (y/n, default: n)"
read -r change_dir
if [ "$change_dir" = "y" ]; then
    echo "Enter new directory path:"
    read -r INSTALL_DIR
fi

# Create directory if not exists
echo -e "${BLUE}Creating installation directory...${NC}"
sudo mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo ""
    echo -e "${YELLOW}IMPORTANT: Please edit .env file with your settings:${NC}"
    echo "  1. Database password (DB_PASSWORD)"
    echo "  2. Secret key (SECRET_KEY)"
    echo "  3. Email configuration (if needed)"
    echo "  4. Other settings as needed"
    echo ""
    echo "Edit .env now? (y/n)"
    read -r edit_env
    if [ "$edit_env" = "y" ]; then
        nano .env || vi .env
    fi
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Create necessary directories
echo -e "${BLUE}Creating necessary directories...${NC}"
sudo mkdir -p uploads logs config/factories
sudo chmod -R 755 uploads logs config
echo -e "${GREEN}✓ Directories created${NC}"

# Pull Docker images
echo ""
echo -e "${BLUE}Pulling Docker images...${NC}"
docker-compose pull

# Build images
echo ""
echo -e "${BLUE}Building Docker images...${NC}"
docker-compose build

# Start services
echo ""
echo -e "${BLUE}Starting services...${NC}"
docker-compose up -d

# Wait for services to be ready
echo -e "${BLUE}Waiting for services to start...${NC}"
sleep 10

# Check service status
echo ""
echo -e "${BLUE}Checking service status...${NC}"
docker-compose ps

# Get Synology IP
SYNOLOGY_IP=$(hostname -I | awk '{print $1}')

echo ""
echo "=========================================="
echo -e "${GREEN}Installation completed successfully!${NC}"
echo "=========================================="
echo ""
echo -e "${BLUE}Access the application:${NC}"
echo "  - Frontend: http://${SYNOLOGY_IP}:3000"
echo "  - Backend API: http://${SYNOLOGY_IP}:8000"
echo "  - API Docs: http://${SYNOLOGY_IP}:8000/api/docs"
echo ""
echo -e "${BLUE}Default credentials:${NC}"
echo "  - Username: admin"
echo "  - Password: admin123"
echo "  ${RED}IMPORTANT: Change these credentials immediately!${NC}"
echo ""
echo -e "${BLUE}Useful commands:${NC}"
echo "  - View logs: docker-compose logs -f"
echo "  - Stop services: docker-compose stop"
echo "  - Start services: docker-compose start"
echo "  - Restart services: docker-compose restart"
echo "  - Remove services: docker-compose down"
echo ""
echo -e "${BLUE}Configuration files:${NC}"
echo "  - .env: ${INSTALL_DIR}/.env"
echo "  - Factory configs: ${INSTALL_DIR}/config/factories/"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Change default admin password"
echo "  2. Configure factory settings in config/factories/"
echo "  3. Set up email notifications in .env"
echo "  4. Configure backup schedule"
echo ""
echo -e "${GREEN}Thank you for using UNS-ClaudeJP!${NC}"
echo "For support: support@uns-kikaku.com"
echo "=========================================="
