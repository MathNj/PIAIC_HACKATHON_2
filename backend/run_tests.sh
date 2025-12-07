#!/bin/bash
#
# Test runner script for TODO API Backend
#
# Usage:
#   ./run_tests.sh              # Run all tests
#   ./run_tests.sh auth         # Run only auth tests
#   ./run_tests.sh tasks        # Run only task tests
#   ./run_tests.sh -v           # Verbose output
#   ./run_tests.sh --cov        # With coverage report

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}  TODO API Test Suite${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Navigate to backend directory
cd "$(dirname "$0")"

# Check if pytest is installed
if ! python -m pytest --version > /dev/null 2>&1; then
    echo -e "${YELLOW}pytest not found. Installing test dependencies...${NC}"
    pip install -q pytest pytest-asyncio httpx
fi

# Parse arguments
PYTEST_ARGS="-v"
RUN_COV=false

for arg in "$@"; do
    case $arg in
        --cov|--coverage)
            RUN_COV=true
            ;;
        auth)
            PYTEST_ARGS="$PYTEST_ARGS -m auth"
            ;;
        tasks)
            PYTEST_ARGS="$PYTEST_ARGS -m tasks"
            ;;
        integration)
            PYTEST_ARGS="$PYTEST_ARGS -m integration"
            ;;
        -v|--verbose)
            PYTEST_ARGS="$PYTEST_ARGS -vv"
            ;;
        *)
            ;;
    esac
done

# Add coverage if requested
if [ "$RUN_COV" = true ]; then
    echo -e "${YELLOW}Installing coverage tools...${NC}"
    pip install -q pytest-cov
    PYTEST_ARGS="$PYTEST_ARGS --cov=app --cov-report=html --cov-report=term"
fi

# Run tests
echo -e "${GREEN}Running tests...${NC}"
echo ""

python -m pytest $PYTEST_ARGS

# Show results
echo ""
if [ $? -eq 0 ]; then
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}  ✓ All tests passed!${NC}"
    echo -e "${GREEN}================================${NC}"

    if [ "$RUN_COV" = true ]; then
        echo ""
        echo -e "${BLUE}Coverage report generated at: htmlcov/index.html${NC}"
    fi
else
    echo -e "${YELLOW}================================${NC}"
    echo -e "${YELLOW}  ✗ Some tests failed${NC}"
    echo -e "${YELLOW}================================${NC}"
    exit 1
fi
