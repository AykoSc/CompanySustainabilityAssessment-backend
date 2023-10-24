"""
The base logger being used throughout this project.
"""

import logging

logging.basicConfig(
    level=logging.INFO,
    datefmt="%d.%m.%y %H:%M:%S",
    format="%(asctime)s | %(levelname)s | %(message)s",
    force=True
)

logger = logging.getLogger(__name__)
