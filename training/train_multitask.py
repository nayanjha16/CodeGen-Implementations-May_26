#!/usr/bin/env python3
"""Fine-tune Qwen multi-task checkpoint (NL2Py + Code2Doc + comments + Java2Py replay)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from train_base import main

if __name__ == "__main__":
    main()
