import logging
import os
import sys
from datetime import datetime

class UnifiedLogger:
    def __init__(self, log_dir="logs"):
        os.makedirs(log_dir, exist_ok=True)

        # Derive a descriptive prefix from the entry-point script name so each
        # subprocess gets its own clearly labelled file, e.g.:
        #   finetune_unified_20260711_141648.log
        #   run_multi_task_inference_20260711_141922.log
        script_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = os.path.join(log_dir, f"{script_name}_{ts}.log")

        fmt = logging.Formatter('%(asctime)s [%(levelname)-7s] %(message)s')

        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(fmt)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.WARNING)   # terminal: warnings/errors only
        stream_handler.setFormatter(fmt)

        self.logger = logging.getLogger("Pipeline")
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)
        self.logger.propagate = False

    @staticmethod
    def _fmt_stats(stats):
        if not stats:
            return ""
        return "  " + "  ".join(f"{k}={v}" for k, v in stats.items())

    def record(self, stage, action, input_data=None, output_data=None, stats=None):
        self.logger.info(f"[{stage}] {action}{self._fmt_stats(stats)}")
        if input_data:
            self.logger.info(f"  >> INPUT  : {str(input_data)[:1000]}")
        if output_data:
            self.logger.info(f"  >> OUTPUT : {str(output_data)[:1000]}")

    def info(self, stage, action, stats=None):
        self.logger.info(f"[{stage}] {action}{self._fmt_stats(stats)}")

    def warning(self, stage, action, stats=None):
        self.logger.warning(f"[{stage}] {action}{self._fmt_stats(stats)}")

    def error(self, stage, action, stats=None):
        self.logger.error(f"[{stage}] {action}{self._fmt_stats(stats)}")

# Global instance — filename is set automatically from sys.argv[0] at import time
pipeline_logger = UnifiedLogger()
