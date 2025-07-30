"""
Pytest configuration and fixtures for DiaNav test suite
"""

import pytest
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture(scope="session")
def test_data_dir():
    """Provide test data directory."""
    return project_root / "tests" / "data"

@pytest.fixture(scope="session")
def sample_dtc_data():
    """Provide sample DTC data for testing."""
    return {
        "P0300": {
            "code": "P0300",
            "description": "Random/Multiple Cylinder Misfire Detected",
            "category": "Engine",
            "severity": "High"
        },
        "P0171": {
            "code": "P0171",
            "description": "System Too Lean (Bank 1)",
            "category": "Fuel System",
            "severity": "Medium"
        }
    }

@pytest.fixture(scope="session")
def mock_ollama_response():
    """Provide mock Ollama response for testing."""
    return {
        "response": "This is a sample AI response for testing purposes.",
        "model": "llama3.2:3b",
        "created_at": "2024-01-01T00:00:00Z"
    }

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment variables."""
    os.environ["DIANAV_MODE"] = "test"
    os.environ["DIANAV_AUTH_ENABLED"] = "false"
    yield
    # Cleanup
    if "DIANAV_MODE" in os.environ:
        del os.environ["DIANAV_MODE"] 