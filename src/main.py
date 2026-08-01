"""Command-line entry point for the NL -> Java -> C# code generation pipeline.

Coordinates training, inference and evaluation; contains no implementation
logic of its own.

Examples:
    python main.py train --stage both
    python main.py infer "write a function to check if a number is prime"
    python main.py evaluate
"""
import argparse
import json

from config.config import CFG
from utils.logger import logger


def _train(args: argparse.Namespace) -> None:
    if args.stage in ("1", "both"):
        from models.train_java_model import train_stage1
        logger.info("Stage 1 result: %s", train_stage1())

    if args.stage in ("2", "both"):
        from models.train_translation_model import train_stage2
        logger.info("Stage 2 result: %s", train_stage2())


def _infer(args: argparse.Namespace) -> None:
    from inference.pipeline import CodeGenPipeline

    pipeline = CodeGenPipeline(
        stage1_repo=args.stage1_repo, stage2_repo=args.stage2_repo)
    result = pipeline.generate_csharp_from_nl(args.prompt)
    print(json.dumps(result, indent=2))


def _evaluate(args: argparse.Namespace) -> None:
    from evaluation.evaluate import run_full_evaluation

    report = run_full_evaluation(
        stage1_repo=args.stage1_repo, stage2_repo=args.stage2_repo)
    print(json.dumps(report, indent=2, default=str))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="NL -> Java -> C# code generation pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    train_parser = subparsers.add_parser(
        "train", help="Train Stage 1 and/or Stage 2 LoRA adapters")
    train_parser.add_argument(
        "--stage", choices=["1", "2", "both"], default="both")
    train_parser.set_defaults(func=_train)

    infer_parser = subparsers.add_parser(
        "infer", help="Run NL -> Java -> C# inference on a prompt")
    infer_parser.add_argument("prompt", type=str)
    infer_parser.add_argument(
        "--stage1-repo", dest="stage1_repo", default=CFG.HF_REPO)
    infer_parser.add_argument(
        "--stage2-repo", dest="stage2_repo", default=CFG.HF_REPO_STAGE2)
    infer_parser.set_defaults(func=_infer)

    eval_parser = subparsers.add_parser(
        "evaluate", help="Evaluate the fine-tuned pipeline")
    eval_parser.add_argument(
        "--stage1-repo", dest="stage1_repo", default=CFG.HF_REPO)
    eval_parser.add_argument(
        "--stage2-repo", dest="stage2_repo", default=CFG.HF_REPO_STAGE2)
    eval_parser.set_defaults(func=_evaluate)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
