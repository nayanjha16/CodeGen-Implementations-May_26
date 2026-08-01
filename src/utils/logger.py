"""Structured logging setup shared across the whole pipeline."""
import logging


def configure_logging(name: str = "CodeGenPipeline", level: int = logging.INFO) -> logging.Logger:
    """Configure the root logger once and return a named child logger.

    Safe to call repeatedly (``force=True`` resets existing handlers).
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
        force=True,
    )
    return logging.getLogger(name)


logger = configure_logging()
