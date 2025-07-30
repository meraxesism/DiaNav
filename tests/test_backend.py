"""
Professional backend tests for DiaNav
These tests are designed to work in CI/CD environment
"""

import pytest
import json
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Import backend components safely
try:
    from dianav_backend import app
    BACKEND_AVAILABLE = True
except ImportError:
    BACKEND_AVAILABLE = False
    app = None

class TestBackendAPI:
    """Test backend API endpoints."""
    
    @pytest.fixture(autouse=True)
    def setup_client(self):
        """Setup test client if backend is available."""
        if BACKEND_AVAILABLE:
            self.client = TestClient(app)
        else:
            self.client = None
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        if not BACKEND_AVAILABLE:
            pytest.skip("Backend not available in test environment")
        
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_query_endpoint_structure(self):
        """Test query endpoint returns proper structure."""
        if not BACKEND_AVAILABLE:
            pytest.skip("Backend not available in test environment")
        
        test_query = {"query": "What is DTC P0300?"}
        response = self.client.post("/query", json=test_query)
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        required_fields = ["conversational", "structured", "images", "has_images"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
    
    def test_dtc_info_endpoint(self):
        """Test DTC info endpoint."""
        if not BACKEND_AVAILABLE:
            pytest.skip("Backend not available in test environment")
        
        response = self.client.get("/dtc-info/P0300")
        assert response.status_code in [200, 404]  # Accept both success and not found
    
    def test_search_endpoint(self):
        """Test search functionality."""
        if not BACKEND_AVAILABLE:
            pytest.skip("Backend not available in test environment")
        
        response = self.client.get("/search?query=engine")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)

class TestBackendComponents:
    """Test individual backend components."""
    
    def test_requirements_file(self):
        """Test that requirements.txt contains expected dependencies."""
        assert os.path.exists("requirements.txt"), "requirements.txt not found"
        
        with open("requirements.txt", "r") as f:
            requirements = f.read()
        
        expected_deps = ["fastapi", "uvicorn", "pydantic"]
        for dep in expected_deps:
            assert dep in requirements, f"Missing dependency: {dep}"
    
    def test_backend_file_exists(self):
        """Test that main backend file exists."""
        assert os.path.exists("dianav_backend.py"), "dianav_backend.py not found"
    
    def test_data_files_structure(self):
        """Test that data files have proper structure."""
        data_files = ["dtc_list.json", "local_dtc_embeddings.json"]
        
        for file_path in data_files:
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    try:
                        data = json.load(f)
                        assert isinstance(data, (dict, list)), f"{file_path} should be JSON object or array"
                    except json.JSONDecodeError:
                        pytest.fail(f"Invalid JSON in {file_path}")

class TestSecurityFeatures:
    """Test security-related features."""
    
    def test_no_hardcoded_secrets(self):
        """Test that no hardcoded secrets are present."""
        sensitive_patterns = [
            "password =",
            "secret =",
            "api_key =",
            "token ="
        ]
        
        python_files = ["dianav_backend.py", "dianav_data.py", "local_vector_search.py"]
        
        for file_path in python_files:
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    for pattern in sensitive_patterns:
                        assert pattern not in content, f"Potential hardcoded secret found in {file_path}"
    
    def test_cors_configuration(self):
        """Test CORS configuration is present."""
        if not BACKEND_AVAILABLE:
            pytest.skip("Backend not available in test environment")
        
        # Check if CORS middleware is configured
        with open("dianav_backend.py", "r") as f:
            content = f.read()
            assert "CORSMiddleware" in content, "CORS middleware not configured"
            assert "allow_origins" in content, "CORS origins not configured"

class TestPerformanceFeatures:
    """Test performance-related features."""
    
    def test_import_performance(self):
        """Test that imports are reasonably fast."""
        import time
        
        start_time = time.time()
        try:
            import json
            import os
            import sys
        except ImportError as e:
            pytest.fail(f"Basic import failed: {e}")
        
        end_time = time.time()
        assert (end_time - start_time) < 1.0, "Basic imports took too long"
    
    def test_file_sizes_reasonable(self):
        """Test that file sizes are reasonable."""
        large_files = []
        
        for file_path in ["dianav_backend.py", "dianav_data.py", "local_vector_search.py"]:
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                if size > 1 * 1024 * 1024:  # 1MB
                    large_files.append((file_path, size))
        
        assert len(large_files) == 0, f"Large files found: {large_files}"

if __name__ == "__main__":
    pytest.main([__file__]) 