import logging
import sys
import os

DEFAULT_THREADS = 200
DEFAULT_TIMEOUT = 3
DEFAULT_PORT = 37777
DEFAULT_SPLIT = 0

if sys.platform == "win32":
    os.system("")

class CustomFormatter(logging.Formatter):
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    ORANGE = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

    LOG_FORMAT = '[%(asctime)s] [%(levelname)s] %(message)s'

    FORMATS = {
        logging.DEBUG: BLUE + LOG_FORMAT + RESET,
        logging.INFO: BLUE + LOG_FORMAT + RESET,
        25: GREEN + BOLD + LOG_FORMAT + RESET,
        logging.WARNING: ORANGE + LOG_FORMAT + RESET,
        logging.ERROR: RED + BOLD + LOG_FORMAT + RESET,
        logging.CRITICAL: RED + BOLD + LOG_FORMAT + RESET,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, self.LOG_FORMAT)
        formatter = logging.Formatter(log_fmt, datefmt='%H:%M:%S')
        return formatter.format(record)

logging.addLevelName(25, 'GOOD')
def good(self, message, *args, **kws):
    if self.isEnabledFor(25):
        self._log(25, message, args, **kws)
logging.Logger.good = good

logger = logging.getLogger("DahuaBrute")
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(CustomFormatter())
    logger.addHandler(ch)
