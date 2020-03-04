import logging
from Logger import Logger

logger = Logger()
logger.setup_testing()

test_logger = logging.getLogger(__name__)
test_logger.debug("TEST DEBUG")
test_logger.info("TEST INFO")
test_logger.warning("TEST WARNING")
test_logger.error("TEST ERROR")
