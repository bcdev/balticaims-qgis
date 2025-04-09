import logging

FORMAT = "%(asctime)s [%(levelname)s]\t%(message)s"
fmt = "%(asctime)s [%(levelname)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def get_logger() -> logging.Logger:
    logging.basicConfig(format=fmt, level=logging.INFO, datefmt=DATE_FORMAT)
    return logging.getLogger()
