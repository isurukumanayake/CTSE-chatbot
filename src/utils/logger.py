import logging
import sys
from pathlib import Path
from config import Config

def setup_logger() -> logging.Logger:
    """Setup application logger"""
    
    # Create logs directory if it doesn't exist
    Config.LOGS_DIR.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format=Config.LOG_FORMAT,
        handlers=[
            logging.FileHandler(Config.LOGS_DIR / "app.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger("ctse_chatbot")
    logger.info("Logger initialized")
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    return logging.getLogger(f"ctse_chatbot.{name}")
