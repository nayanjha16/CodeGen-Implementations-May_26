"""Python execution sandbox for measuring execution accuracy (HumanEval-style).

Given a problem (prompt + test + entry_point) and a candidate completion, assemble a runnable
program, execute it in an isolated child process, and report whether it passed.

Design notes (why this is NOT a copy-paste of openai/human-eval):
 * The upstream harness uses signal.SIGALRM and resource.setrlimit, which DO NOT EXIST on
   Windows. We gate those behind capability checks and rely on a subprocess wall-clock timeout
   plus a psutil memory/CPU watchdog instead, so the SAME code runs on the Windows dev box and
   on Kaggle/Colab Linux.
 * The assembled program MUST end with an explicit `check(entry_point)` call, otherwise the test
   function is defined-but-never-run and every candidate spuriously "passes" (a silent
   false-positive). Gate V5 (tests/test_sandbox_gate_v5.py) exists to catch exactly this.

SECURITY: this runs untrusted, model-generated code. The process isolation here (separate
process, timeout, memory cap, temp cwd) is a guard rail, NOT a real sandbox. On a dev machine
treat every candidate as hostile; for heavy runs prefer an ephemeral VM/container or Kaggle's
disposable kernel.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import textwrap
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

try:
   import psutil  # present on the dev box (7.1.0); used for the memory watchdog + tree-kill
except ImportError:  # pragma: no cover
   psutil = None


class Outcome(str, Enum):
   PASSED = "passed"
   WRONG_OUTPUT = "wrong_output"      # assertion failed -> logic wrong
   RUNTIME_ERROR = "runtime_error"    # raised an exception
   COMPILE_ERROR = "compile_error"    # syntax error (Python: caught at exec/import)
   TIMEOUT = "timeout"                # exceeded wall-clock limit (incl. infinite loops)
   OOM = "oom"                        # exceeded the memory cap
   HARNESS_ERROR = "harness_error"    # something wrong on our side, not the candidate


@dataclass
class ExecResult:
   task_id: str
   completion_id: int
   outcome: Outcome
   detail: str = ""
   runtime_s: float = 0.0

   @property
   def passed(self) -> bool:
       return self.outcome == Outcome.PASSED


# A small runner template. The candidate program is written to its own file and executed; this
# keeps the parent process clean and lets us hard-kill on timeout/OOM.
_RUNNER = """\
import sys, builtins
# defense-in-depth: neutralise the most obvious foot-guns. NOT a real sandbox.
import os as _os
_os.system = lambda *a, **k: (_ for _ in ()).throw(PermissionError("os.system blocked"))
try:
   import subprocess as _sp
   _sp.Popen = lambda *a, **k: (_ for _ in ()).throw(PermissionError("subprocess blocked"))
except Exception:
   pass

{program}
"""


def build_program(prompt: str, completion: str, test: str, entry_point: str) -> str:
   """Assemble prompt + completion + test, ending in the all-important check() call."""
   body = f"{prompt}{completion}\n\n{test}\n\ncheck({entry_point})\n"
   return _RUNNER.format(program=body)


def _kill_tree(pid: int) -> None:
   if psutil is None:
       return
   try:
       parent = psutil.Process(pid)
       for child in parent.children(recursive=True):
           try:
               child.kill()
           except psutil.NoSuchProcess:
               pass
       parent.kill()
   except psutil.NoSuchProcess:
       pass


def _memory_watchdog(proc: subprocess.Popen, limit_mb: int, flag: dict, poll_s: float = 0.05):
   """Poll RSS; if it exceeds the cap, kill the tree and record an OOM. Replaces setrlimit."""
   if psutil is None:
       return
   try:
       ps = psutil.Process(proc.pid)
   except psutil.NoSuchProcess:
       return
   limit_bytes = limit_mb * 1024 * 1024
   while proc.poll() is None:
       try:
           rss = ps.memory_info().rss
           for child in ps.children(recursive=True):
               try:
                   rss += child.memory_info().rss
               except psutil.NoSuchProcess:
                   pass
           if rss > limit_bytes:
               flag["oom"] = True
               _kill_tree(proc.pid)
               return
       except psutil.NoSuchProcess:
           return
       time.sleep(poll_s)


def check_correctness(
   problem: dict,
   completion: str,
   timeout_s: float = 10.0,
   memory_mb: int = 512,
   completion_id: int = 0,
) -> ExecResult:
   """Run one candidate. `problem` needs keys: task_id, prompt, test, entry_point."""
   task_id = problem.get("task_id", "unknown")
   program = build_program(
       problem["prompt"], completion, problem["test"], problem["entry_point"]
   )

   with tempfile.TemporaryDirectory() as workdir:
       src_path = os.path.join(workdir, "candidate.py")
       with open(src_path, "w", encoding="utf-8") as f:
           f.write(program)

       flag: dict = {"oom": False}
       start = time.time()
       try:
           proc = subprocess.Popen(
               [sys.executable, "-I", src_path],  # -I: isolated, ignore env/user site
               cwd=workdir,
               stdout=subprocess.PIPE,
               stderr=subprocess.PIPE,
               stdin=subprocess.DEVNULL,
           )
       except Exception as e:  # pragma: no cover
           return ExecResult(task_id, completion_id, Outcome.HARNESS_ERROR, str(e))

       watcher = threading.Thread(
           target=_memory_watchdog, args=(proc, memory_mb, flag), daemon=True
       )
       watcher.start()

       try:
           _out, err = proc.communicate(timeout=timeout_s)  # drains pipes -> no deadlock
       except subprocess.TimeoutExpired:
           _kill_tree(proc.pid)
           proc.communicate()
           return ExecResult(task_id, completion_id, Outcome.TIMEOUT,
                             f"exceeded {timeout_s}s", time.time() - start)

       runtime = time.time() - start
       if flag["oom"]:
           return ExecResult(task_id, completion_id, Outcome.OOM,
                             f"exceeded {memory_mb}MB", runtime)

       if proc.returncode == 0:
           return ExecResult(task_id, completion_id, Outcome.PASSED, "", runtime)

       stderr = (err or b"").decode("utf-8", "replace")
       return ExecResult(task_id, completion_id, _classify(stderr), _last_line(stderr), runtime)


def _classify(stderr: str) -> Outcome:
   if "SyntaxError" in stderr or "IndentationError" in stderr:
       return Outcome.COMPILE_ERROR
   if "AssertionError" in stderr:
       return Outcome.WRONG_OUTPUT
   if "MemoryError" in stderr:
       return Outcome.OOM
   return Outcome.RUNTIME_ERROR


def _last_line(stderr: str) -> str:
   lines = [ln for ln in stderr.strip().splitlines() if ln.strip()]
   return lines[-1][:200] if lines else ""
