import logging


logger = logging.getLogger("seat-availability")
logger.setLevel(logging.INFO)


formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)


if not logger.hasHandlers():
    logger.addHandler(console_handler)
