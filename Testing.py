from Logger import Logger
import logging

logger = Logger()
logger.setup_testing()

test_logger = logging.getLogger(__name__)
test_logger.error("THIS IS A TEST ERROR")
