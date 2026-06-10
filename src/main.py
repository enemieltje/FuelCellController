import sys
import signal
import logging
from pathlib import Path

from Config import Config
from Database import Database
from Drone import Drone
from Power_System import Power_System
from Server import Server

LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "latest.log"

print("Starting...")
# !../.venv/bin/python

# Keep a file log for later debugging and mirror the same messages to stdout.
LOG_DIR.mkdir(exist_ok=True)
logger = logging.getLogger(__name__)
logging.basicConfig(
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
    level=logging.DEBUG,
)


SERVICES = (
    Config,
    Database,
    Drone,
    Power_System,
    Server,
)


def sigterm_handler(_signo, _stack_frame):
    """Stop services in reverse startup order before the process exits."""
    logger.info("stopping...")
    for service in reversed(SERVICES):
        stop = getattr(service, "stop", None)
        if stop is None:
            continue

        try:
            stop()
        except Exception:
            logger.exception("Failed to stop %s cleanly", service.__name__)

    sys.exit(0)


if __name__ == "__main__":
    # systemd and service managers usually send SIGTERM during shutdown.
    signal.signal(signal.SIGTERM, sigterm_handler)

    logger.info("starting")
    try:
        for service in SERVICES:
            service.start()
    finally:
        sigterm_handler(signal.SIGTERM, 0)
