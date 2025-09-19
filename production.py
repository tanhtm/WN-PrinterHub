# Production deployment script for WN-PrinterHub
# Suitable for systemd service or production environments

import os
import sys
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_production_logging():
    """Setup production-grade logging."""
    log_level = os.getenv("WN_LOG_LEVEL", "INFO").upper()
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(process)d - %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("/var/log/wn-printerhub.log") if os.access("/var/log", os.W_OK) else logging.NullHandler()
        ]
    )

def main():
    """Production entry point."""
    setup_production_logging()
    logger = logging.getLogger("wn-printerhub.production")
    
    try:
        logger.info("Starting WN-PrinterHub in production mode...")
        
        # Import here to ensure proper setup
        import uvicorn
        from app.main import app
        from app.config import config
        
        # Production configuration
        uvicorn.run(
            app,
            host=config.host,
            port=config.port,
            log_level=config.log_level.lower(),
            access_log=True,
            workers=1,  # Single worker for TCP connection management
            loop="asyncio"
        )
        
    except Exception as e:
        logger.error(f"Failed to start WN-PrinterHub: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()