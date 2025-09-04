#!/bin/bash
# BIGPIAI Startup Script
# Simple script to start the application in different modes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "run.py" ]; then
    print_error "run.py not found. Please run this script from the BIGPIAI project root directory."
    exit 1
fi

# Function to show usage
show_usage() {
    echo "Usage: $0 [dev|prod|test]"
    echo ""
    echo "Commands:"
    echo "  dev   - Start development server (default)"
    echo "  prod  - Start production server"
    echo "  test  - Test environment configuration"
    echo "  help  - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 dev    # Start development server"
    echo "  $0 prod   # Start production server"
    echo "  $0 test   # Test environment setup"
}

# Parse command line arguments
MODE=${1:-dev}

case $MODE in
    "dev"|"development")
        print_status "Starting BIGPIAI in development mode..."
        python3 run_local.py
        ;;
    "prod"|"production")
        print_status "Starting BIGPIAI in production mode..."
        python3 run_production.py
        ;;
    "test"|"check")
        print_status "Testing environment configuration..."
        python3 test_env.py
        ;;
    "help"|"-h"|"--help")
        show_usage
        ;;
    *)
        print_error "Unknown command: $MODE"
        echo ""
        show_usage
        exit 1
        ;;
esac