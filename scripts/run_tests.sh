#!/usr/bin/env bash
# ============================================================
# QuickUtils API Directory — Local Test Runner (Bash)
# Runs the full test suite inside Docker. No local installs needed.
# ============================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

header() { echo -e "\n${CYAN}=== $1 ===${NC}"; }
success() { echo -e "  ${GREEN}✓ $1${NC}"; }
fail() { echo -e "  ${RED}✗ $1${NC}"; }

show_help() {
    echo "QuickUtils API Directory — Local Development Scripts"
    echo ""
    echo "Usage:"
    echo "  ./scripts/run_tests.sh           Run full test suite with coverage"
    echo "  ./scripts/run_tests.sh build      Build the static site"
    echo "  ./scripts/run_tests.sh serve      Build and serve on http://localhost:8000"
    echo "  ./scripts/run_tests.sh coverage   Run tests with HTML coverage report"
    echo "  ./scripts/run_tests.sh help       Show this help message"
    echo ""
    echo "Prerequisites: Docker must be running."
}

# Check Docker
check_docker() {
    if ! docker version &>/dev/null; then
        fail "Docker is not running. Please start Docker."
        exit 1
    fi
    success "Docker is available"
}

CMD="${1:-test}"

case "$CMD" in
    help|-h|--help)
        show_help
        exit 0
        ;;
    serve)
        check_docker
        header "Building and Serving Site"
        echo -e "  ${YELLOW}Site will be available at http://localhost:8000${NC}"
        echo -e "  ${YELLOW}Press Ctrl+C to stop.${NC}"
        docker compose up --build serve
        ;;
    build)
        check_docker
        header "Building Static Site"
        docker compose run --rm build
        if [ $? -eq 0 ]; then
            success "Build completed. Output in dist/"
            echo -e "  ${YELLOW}Total HTML pages: $(find dist/ -name '*.html' 2>/dev/null | wc -l)${NC}"
        else
            fail "Build failed."
            exit 1
        fi
        ;;
    coverage)
        check_docker
        header "Running Tests with HTML Coverage Report"
        docker compose run --rm test python -m pytest tests/ -v \
            --cov=scripts \
            --cov-report=html \
            --cov-report=term-missing \
            --cov-fail-under=90
        if [ $? -eq 0 ]; then
            success "Tests passed! Open htmlcov/index.html for the report."
        else
            fail "Tests failed or coverage below 90%."
            exit 1
        fi
        ;;
    test|*)
        check_docker
        header "Running Full Test Suite"
        docker compose run --rm test
        if [ $? -eq 0 ]; then
            success "All tests passed with ≥90% coverage!"
        else
            fail "Tests failed or coverage below 90%."
            exit 1
        fi
        ;;
esac
