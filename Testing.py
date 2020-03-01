from Logger import Logger
import logging

logger = Logger()
logger.setup_testing()

test_logger = logging.getLogger(__name__)
test_logger.debug("THIS IS A TEST DEBUG")
test_logger.info("THIS IS A TEST INFO")
test_logger.warning("THIS IS A TEST WARNING")
test_logger.error("THIS IS A TEST ERROR")
test_logger.warning("THIS IS AN EXTRA TEST WARNING")
