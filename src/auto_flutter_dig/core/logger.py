from logging import basicConfig, getLogger

__all__ = ["log"]
basicConfig(
    # filename="aflutter.log",
    # filemode="wt",
    format="%(asctime)s %(filename)s@%(lineno)03d [%(levelname)s]: %(message)s",
)

log = getLogger(__name__)
