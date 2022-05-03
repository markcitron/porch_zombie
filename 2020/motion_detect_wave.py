#!/usr/bin/python3

import logging
import logging.handlers as handlers

def main():
    # Logging
    logname = "motion_log.log"
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    logHandler = handlers.RotatingFileHandler(logname, maxBytes=10000000, backupCount=5)
    logHandler.setLevel(logging.INFO)
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)

if __name__ == "__main__":
    main()
