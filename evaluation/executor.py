"""Submit generated code to Docker sandbox and collect execution results."""

import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SANDBOX_IMAGE = "code-sandbox"
SANDBOX_DIR = PROJECT_ROOT / "sandbox"


class CodeExecutor:
    def __init__(
        self,
        image: str = SANDBOX_IMAGE,
        timeout: int = 10,
        memory_limit: str = "256m",
        use_docker: bool = True,
    ):
        self.image = image
        self.timeout = timeout
        self.memory_limit = memory_limit
        self.use_docker = use_docker
        self._docker_available = self._check_docker() if use_docker else False

    def _check_docker(self) -> bool:
        try:
            result = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def execute(
        self,
        code: str,
        test_cases: list[dict] | None = None,
    ) -> dict:
        payload = {
            "code": code,
            "test_cases": test_cases or [],
            "timeout": self.timeout,
        }

        if self._docker_available:
            return self._execute_docker(payload)
        return self._execute_local(payload)

    def _execute_docker(self, payload: dict) -> dict:
        import docker

        client = docker.from_env()
        try:
            container = client.containers.run(
                self.image,
                stdin_open=True,
                detach=True,
                mem_limit=self.memory_limit,
                network_disabled=True,
                read_only=True,
                tmpfs={"/tmp": "size=64m"},
            )
            try:
                sock = container.attach_socket(params={"stdin": 1, "stream": 1})
                sock._sock.sendall(json.dumps(payload).encode())
                sock._sock.shutdown(1)

                exit_code = container.wait(timeout=self.timeout + 5)
                logs = container.logs(stdout=True, stderr=True).decode("utf-8", errors="replace")

                try:
                    lines = [l for l in logs.strip().split("\n") if l.strip().startswith("{")]
                    result = json.loads(lines[-1]) if lines else {"passed": False, "error": logs}
                except (json.JSONDecodeError, IndexError):
                    result = {
                        "passed": exit_code.get("StatusCode", 1) == 0,
                        "stdout": logs,
                        "stderr": "",
                        "error": None if exit_code.get("StatusCode", 1) == 0 else logs,
                    }
                return result
            finally:
                container.remove(force=True)
        except Exception as e:
            return {
                "passed": False,
                "stdout": "",
                "stderr": str(e),
                "error": str(e),
            }

    def _execute_local(self, payload: dict) -> dict:
        """Fallback: run sandbox/runner.py locally without Docker."""
        runner = SANDBOX_DIR / "runner.py"
        try:
            proc = subprocess.run(
                ["python", str(runner)],
                input=json.dumps(payload),
                capture_output=True,
                text=True,
                timeout=self.timeout + 5,
            )
            try:
                return json.loads(proc.stdout.strip().split("\n")[-1])
            except (json.JSONDecodeError, IndexError):
                return {
                    "passed": proc.returncode == 0,
                    "stdout": proc.stdout,
                    "stderr": proc.stderr,
                    "error": proc.stderr if proc.returncode != 0 else None,
                }
        except subprocess.TimeoutExpired:
            return {"passed": False, "error": "Local execution timed out"}
        except Exception as e:
            return {"passed": False, "error": str(e)}

    def build_image(self) -> bool:
        """Build the sandbox Docker image."""
        try:
            subprocess.run(
                ["docker", "build", "-t", self.image, str(SANDBOX_DIR)],
                check=True,
                capture_output=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Failed to build sandbox image: {e}")
            return False
