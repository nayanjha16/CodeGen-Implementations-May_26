"""
============================================================
RepoCoder Studio
logger.py
============================================================

Project Logging Framework

Engineering Specification
-------------------------
Section 10
Software Architecture

Purpose
-------
Provides centralized logging for the entire project.

Every module must use this logger instead of print() for
important runtime events.

Benefits
--------
✓ Consistent console output

✓ Automatic log file generation

✓ Timestamped execution

✓ Runtime debugging

✓ Easy experiment tracking

Stage Learnings
---------------
Stage 1

Debugging notebook execution became difficult because
important messages were mixed with notebook output.

Stage 2

Training failures required preserving logs after Colab
runtime termination.

Stage 3

Corpus validation produced thousands of messages.

A centralized logger became essential.

Author
------
RepoCoder Studio
"""

# ============================================================
# Imports
# ============================================================

import logging
import os
import sys
from pathlib import Path
from typing import Optional

from src.config import CONFIG


# ============================================================
# Project Logger
# ============================================================

class ProjectLogger:
    """
    ===========================================================
    Project Logger

    Purpose
    -------
    Central logging utility for RepoCoder Studio.

    Every project component should obtain its logger through
    this class.

    Responsibilities
    ----------------
    • Configure console logging

    • Configure file logging

    • Prevent duplicate handlers

    • Standardize log format

    • Create log directory automatically

    Example
    -------
    logger = ProjectLogger(CONFIG)

    log = logger.get_logger(__name__)

    log.info("Loading XLCoST")
    """

    def __init__(self, config=CONFIG):

        self.config = config

        self.logger = logging.getLogger("RepoCoderStudio")

        self.logger.setLevel(logging.INFO)

        self.logger.propagate = False

        self._configure()

    # --------------------------------------------------------
    # Internal configuration
    # --------------------------------------------------------

    def _configure(self):

        """
        Configures logging.

        This function is intentionally executed only once.

        Duplicate handlers are removed to avoid repeated
        notebook output.
        """

        if self.logger.handlers:
            return

        formatter = logging.Formatter(

            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",

            datefmt="%H:%M:%S"

        )

        # ----------------------------------------------
        # Console logging
        # ----------------------------------------------

        if self.config.logging.log_to_console:

            console = logging.StreamHandler(sys.stdout)

            console.setFormatter(formatter)

            self.logger.addHandler(console)

        # ----------------------------------------------
        # File logging
        # ----------------------------------------------

        if self.config.logging.log_to_file:

            log_dir = self.config.storage.resolve(

                self.config.storage.logs_dir

            )

            os.makedirs(log_dir, exist_ok=True)

            logfile = log_dir / self.config.logging.log_filename

            file_handler = logging.FileHandler(logfile)

            file_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)

    # --------------------------------------------------------
    # Public API
    # --------------------------------------------------------

    def get_logger(self, name: Optional[str] = None):

        """
        Returns a logger.

        Parameters
        ----------
        name

            Optional child logger.

        Returns
        -------

        logging.Logger
        """

        if name is None:

            return self.logger

        return self.logger.getChild(name)


# ============================================================
# Pretty Console Sections
# ============================================================

class SectionPrinter:
    """
    Creates notebook-friendly section headers.

    Example
    -------

    ============================================================
    Candidate Corpus Builder
    ============================================================
    """

    WIDTH = 68

    @staticmethod
    def header(title: str):

        line = "=" * SectionPrinter.WIDTH

        print()

        print(line)

        print(title)

        print(line)

    @staticmethod
    def subheader(title: str):

        line = "-" * SectionPrinter.WIDTH

        print()

        print(line)

        print(title)

        print(line)


# ============================================================
# Runtime Summary Printer
# ============================================================

class SummaryPrinter:
    """
    Prints aligned runtime summaries.

    Example

    Rows Loaded        : 8945

    Approved           : 8701

    Runtime            : 00:02:31
    """

    @staticmethod
    def print_summary(title, values):

        SectionPrinter.header(title)

        for key, value in values.items():

            print(f"{key:<28}: {value}")

        print("=" * SectionPrinter.WIDTH)


# ============================================================
# Global logger instance
# ============================================================

LOGGER = ProjectLogger(CONFIG)

LOG = LOGGER.get_logger("Main")