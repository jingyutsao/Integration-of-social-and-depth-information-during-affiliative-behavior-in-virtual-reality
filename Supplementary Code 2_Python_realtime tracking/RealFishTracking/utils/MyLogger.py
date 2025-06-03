# -*- coding: utf-8 -*-
"""Define the logger to be used in the whole RealFishTracking program.

This module defines the logger that will be used in the RealFishTracking 
program. By definition, two logging handler will be generated. One for printing
message to the stdout during experiment, and the other for printing message to 
the log file. Note that only message-level higher than INFO will be printed 
during experiment.

Example:
    To use the logger defined here, import this module in the import section:

        from MyLogger import logger

    After importing, you can use the instance logger directly, like:

        logger.debug("print some debug message to the file.")
        logger.info("print some info to the stdout and the file.")
        logger.warning("user should notice, but it's not something terrible.")
        logger.error("user should check the setup or code.")
        logger.critical("user should really worry if you use this.")

Attributes:
    no attributes.

TODO:

"""
import logging
import sys

# Instantiate a logger immediately when importing this module
logger = logging.getLogger()

# Setup properties of the logger
formatter = logging.Formatter("%(asctime)s - [%(levelname)s] %(message)s")
logger.setLevel(logging.DEBUG)

# 1st logging handler -> print information to the stdout, user can get information while doing experiment.
stdHandler = logging.StreamHandler(sys.stdout)
stdHandler.setLevel(logging.INFO)
stdHandler.setFormatter(formatter)
logger.addHandler(stdHandler)

# 2nd logging handler -> dump all the debug message to the debug file, user can later check everything in the file.
fileHandler = logging.FileHandler("debug.log", mode='w')
fileHandler.setLevel(logging.DEBUG)
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)


if __name__ == '__main__':
    # Entry point if call it from shell.
    logger.debug('MyLogger main')

else:
    # Entry point if import it to other program
    logger.debug("logger imported.")