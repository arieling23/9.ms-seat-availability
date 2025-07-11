import logging

# Configura el logger global
logger = logging.getLogger("seat-availability")
logger.setLevel(logging.INFO)

# Formato del log
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

# Salida a consola
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Agrega el handler si no existe
if not logger.hasHandlers():
    logger.addHandler(console_handler)
