"""
Logging configuration: INFO+ to file, WARNING+ to console.
"""
import logging
import os
from datetime import datetime


def setup_logging(level: int = logging.INFO) -> str:
    os.makedirs("logs", exist_ok=True)
    log_file = f"logs/recommender_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    fmt = logging.Formatter("%(asctime)s %(levelname)-8s %(name)s — %(message)s")

    root = logging.getLogger()
    root.setLevel(level)

    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    console.setFormatter(fmt)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(fmt)

    root.addHandler(console)
    root.addHandler(file_handler)

    logging.getLogger(__name__).info("Logging initialized → %s", log_file)
    return log_file
