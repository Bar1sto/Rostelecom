import os
import logging
from logging.handlers import TimedRotatingFileHandler


def config_log(service_name: str) -> logging.Logger:
    level = os.getenv("LEVEL", "INFO").upper()
    dir_log = os.getenv("DIR", "logs")
    os.makedirs(dir_log, exist_ok=True)
    
    format = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    formatter = logging.Formatter(format)
    
    file_path = os.path.join(
        dir_log,
        f"{service_name}.log"
    )
    file_handler = TimedRotatingFileHandler(
        file_path,
        when="midnight",
        backupCount=7,
        encoding="utf-8",
        utc=True,
    )
    file_handler.setFormatter(formatter)
    
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    
    root = logging.getLogger()
    root.setLevel(level)
    
    ready = {
        type(i) for i in root.handlers
    }
    if logging.StreamHandler not in ready:
        root.addHandler(console)
    root.addHandler(file_handler)
    
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "aio_pika"):
        log = logging.getLogger(name)
        log.setLevel(level)
        log.addHandler(file_handler)
        
    logger = logging.getLogger(service_name)
    logger.info(
        "Logging configured. file=%s level=%s", 
        file_path,
        level
    )
    return logger