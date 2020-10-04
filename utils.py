import logging


def setup_logging(level=logging.DEBUG):
    logging.basicConfig(
        format='[%(levelname)-7s] %(asctime)s %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        level=level)
