#!/bin/bash
# Container Setup Script for GravityCommit
# This script sets up auto-commit for container environments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}GravityCommit Container Setup${NC}"
echo "=================================="

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo -e "${RED}Error: Not a git repository${NC}"
    echo "Please run this script from the root of your git repository"
    exit 1
fi

# Check if autocommit is installed
if ! command -v autocommit &> /dev/null; then
    echo -e "${RED}Error: autocommit is not installed${NC}"
    echo "Please install GravityCommit first:"
    echo "  pip install gravitycommit"
    exit 1
fi

PROJECT_PATH=$(pwd)
echo -e "${YELLOW}Setting up auto-commit for: ${PROJECT_PATH}${NC}"

# Setup container mode
echo "Setting up container mode..."
autocommit container-setup "$PROJECT_PATH" --interval 5

echo ""
echo -e "${GREEN}Setup complete!${NC}"
echo ""
echo "To start auto-commit:"
echo "  autocommit container-start $PROJECT_PATH"
echo ""
echo "To start in background:"
echo "  autocommit container-start $PROJECT_PATH --background"
echo ""
echo "To stop auto-commit:"
echo "  autocommit container-stop $PROJECT_PATH"
echo ""
echo "To check status:"
echo "  autocommit status $PROJECT_PATH"
