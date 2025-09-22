# Environment Configuration for WN-PrinterHub
"""
Environment variable configuration module.
Handles loading and validation of environment variables.
"""
import os
from typing import List
import logging
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """Configuration class for WN-PrinterHub."""
    
    def __init__(self):
        self.api_token = os.getenv("WN_API_TOKEN", "CHANGE_ME")
        self.use_auth = os.getenv("USE_AUTH", "true").lower() in ("true", "1", "yes", "on")
        self.allowed_origins = self._parse_allowed_origins()
        self.printer_default_port = int(os.getenv("WN_PRINTER_DEFAULT_PORT", "9100"))
        self.host = os.getenv("WN_HOST", "0.0.0.0")
        self.port = int(os.getenv("WN_PORT", "8088"))
        self.log_level = os.getenv("WN_LOG_LEVEL", "INFO").upper()
        
        self._validate_config()
    
    def _parse_allowed_origins(self) -> List[str]:
        """Parse allowed origins from environment variable."""
        origins_str = os.getenv("WN_ALLOWED_ORIGINS", "*")
        if not origins_str:
            return ["*"]
        
        origins = [origin.strip() for origin in origins_str.split(",") if origin.strip()]
        return origins if origins else ["*"]
    
    def _validate_config(self):
        """Validate configuration values."""
        if not self.use_auth:
            logger.warning(
                "WARNING: Authentication is disabled (USE_AUTH=false)! "
                "This should only be used in secure development environments."
            )
        elif self.api_token == "CHANGE_ME":
            logger.warning(
                "WARNING: Using default API token! "
                "Please set WN_API_TOKEN environment variable for security!"
            )
        elif self.api_token and len(self.api_token) < 16:
            logger.warning(
                "WARNING: API token is too short! "
                "Consider using a longer, more secure token."
            )
        
        if not (1024 <= self.port <= 65535):
            raise ValueError(f"Invalid port number: {self.port}. Must be between 1024-65535.")
        
        if not (1 <= self.printer_default_port <= 65535):
            raise ValueError(f"Invalid printer port: {self.printer_default_port}")
        
        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            logger.warning(f"Invalid log level: {self.log_level}. Using INFO.")
            self.log_level = "INFO"
    
    def get_log_level(self) -> int:
        """Get logging level as integer."""
        return getattr(logging, self.log_level, logging.INFO)


# Global configuration instance
config = Config()