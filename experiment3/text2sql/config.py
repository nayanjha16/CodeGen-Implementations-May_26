from dataclasses import dataclass
from pathlib import Path
import yaml

@dataclass
class BenchmarkConfig:
    models: list[dict]
    scenarios: list[str]
    datasets: list[str]
    evaluation: dict

    def model_ids(self) -> list[str]:
        return [m["id"] for m in self.models]

    def model(self, model_id: str) -> dict:
        return next(m for m in self.models if m["id"] == model_id)

    def experiments(self) -> list[dict]:
        out = []
        for m in self.models:
            for s in self.scenarios:
                for d in self.datasets:
                    out.append({"model": m["id"], "scenario": s, "dataset": d})
        return out

def load_config(path: Path) -> BenchmarkConfig:
    raw = yaml.safe_load(Path(path).read_text())
    return BenchmarkConfig(models=raw["models"], scenarios=raw["scenarios"],
                           datasets=raw["datasets"], evaluation=raw["evaluation"])
