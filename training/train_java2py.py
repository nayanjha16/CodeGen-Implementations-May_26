#!/usr/bin/env python3
"""Fine-tune codegen-350M-multi for Java-to-Python translation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from train_base import main

if __name__ == "__main__":
    main()
