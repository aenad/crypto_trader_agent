"""Offline report generation. No network or trading engine is started."""

import argparse
from pathlib import Path

from .report import competition_markdown, metrics_csv
from .repository import ReportRepository


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("data/dashboard"))
    parser.add_argument("--run", default="demo")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    view = ReportRepository(args.root).get(args.run)
    args.output.mkdir(parents=True, exist_ok=True)
    paths = [args.output / ("competition." + extension) for extension in ("json", "md", "csv")]
    if any(path.exists() for path in paths):
        raise FileExistsError("Report files already exist; choose a new output directory")
    for path, content in zip(
        paths,
        [view.model_dump_json(indent=2), competition_markdown(view), metrics_csv(view)],
        strict=True,
    ):
        with path.open("x", encoding="utf-8", newline="") as output:
            output.write(content)
    print(f"Generated {view.source.kind} report; simulated={view.source.simulated}")


if __name__ == "__main__":
    main()
