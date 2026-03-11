# Testing & Quality Assurance

## Overview
This project maintains a strict **90%+ code coverage** requirement. Every build is validated via GitHub Actions before deployment.

## Running Tests
### Docker (Recommended)
```bash
docker compose run --rm test bash -c "pytest tests/ --cov=scripts"
```

### Local Python
```bash
pytest tests/ --cov=scripts
```

## Test Suite Components
- `test_build_directory.py`: Validates HTML generation, RSS, and Search index.
- `test_fetch_data.py`: Validates data normalization and deduplication.
- `test_utils.py`: Validates slugification and DB I/O.
- `test_generate_pins.py`: Smoke tests for Pinterest automation.

## Coverage Policy
Any new features (RSS, Search, etc.) must include corresponding test assertions. Builds will fail in CI if coverage drops below 90%.
