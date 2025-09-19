"""
Test suite for WN-PrinterHub
"""
import pytest
import asyncio
from unittest.mock import Mock, patch
from app.main import app
from app.config import Config
from app.escpos_utils import ESCPOSBuilder, create_receipt
from app.network_utils import validate_ip_address, is_private_ip
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


@pytest.fixture  
def auth_headers():
    """Authentication headers for testing."""
    return {"Authorization": "Bearer CHANGE_ME"}


class TestBasicEndpoints:
    """Test basic endpoints."""
    
    def test_health_endpoint(self, client):
        """Test health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "service" in data
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "WN-PrinterHub"
        assert "endpoints" in data
    
    def test_authentication_required(self, client):
        """Test that authentication is required for protected endpoints."""
        response = client.post("/api/v1/printers/ping", json={"host": "192.168.1.1"})
        assert response.status_code == 401


class TestESCPOSUtils:
    """Test ESC/POS utilities."""
    
    def test_escpos_builder_basic(self):
        """Test basic ESC/POS builder functionality."""
        builder = ESCPOSBuilder()
        result = builder.text("Hello").line("World").build()
        
        assert isinstance(result, bytes)
        assert b"Hello" in result
        assert b"World" in result
        assert b"\x1b@" in result  # Initialize command
    
    def test_escpos_builder_formatting(self):
        """Test ESC/POS builder formatting."""
        builder = ESCPOSBuilder()
        result = (builder
                 .bold(True)
                 .text("Bold Text")
                 .bold(False)
                 .underline(True) 
                 .text("Underlined")
                 .build())
        
        assert b"\x1b\x45\x01" in result  # Bold on
        assert b"\x1b\x45\x00" in result  # Bold off
        assert b"\x1b\x2d\x01" in result  # Underline on
    
    def test_create_receipt(self):
        """Test receipt creation."""
        items = [
            {"name": "Coffee", "qty": 2, "price": 3.50},
            {"name": "Sandwich", "qty": 1, "price": 8.99}
        ]
        
        receipt = create_receipt(
            items, 
            15.99,
            header="Test Store",
            footer="Thank you!"
        )
        
        assert isinstance(receipt, bytes)
        assert b"Coffee" in receipt
        assert b"Test Store" in receipt
        assert b"Thank you!" in receipt


class TestNetworkUtils:
    """Test network utilities."""
    
    def test_validate_ip_address(self):
        """Test IP address validation."""
        assert validate_ip_address("192.168.1.1") == True
        assert validate_ip_address("10.0.0.1") == True
        assert validate_ip_address("256.1.1.1") == False
        assert validate_ip_address("not.an.ip") == False
        assert validate_ip_address("192.168.1") == False
    
    def test_is_private_ip(self):
        """Test private IP detection."""
        assert is_private_ip("192.168.1.1") == True
        assert is_private_ip("10.0.0.1") == True
        assert is_private_ip("172.16.1.1") == True
        assert is_private_ip("8.8.8.8") == False
        assert is_private_ip("1.1.1.1") == False


class TestConfiguration:
    """Test configuration handling."""
    
    def test_config_defaults(self):
        """Test default configuration values."""
        config = Config()
        assert config.printer_default_port == 9100
        assert config.host == "0.0.0.0"
        assert config.port == 8088
    
    @patch.dict("os.environ", {"WN_API_TOKEN": "secure-token-123"})
    def test_config_from_env(self):
        """Test configuration from environment variables.""" 
        config = Config()
        assert config.api_token == "secure-token-123"


@pytest.mark.asyncio
class TestAsyncFunctions:
    """Test async functions."""
    
    async def test_tcp_connection_mock(self):
        """Test TCP connection with mock."""
        from app.main import tcp_connect
        
        # This would need proper mocking in a real test environment
        # For now, just test the function signature
        assert callable(tcp_connect)


if __name__ == "__main__":
    pytest.main([__file__])