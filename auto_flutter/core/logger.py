import logging

logging.basicConfig(
    format="%(asctime)s %(filename)s@%(lineno)03d [%(levelname)s]: %(message)s"
)
log = logging.getLogger(__name__)
