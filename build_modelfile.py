#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE_FILE = ROOT / "Base.Modelfile"
DEFAULT_OUTPUT = ROOT / "Modelfile"
EXCLUDE_FILES = {"Base.Modelfile"}


def list_modes() -> list[Path]:
    return sorted(
        [p for p in ROOT.glob("*.Modelfile") if p.name not in EXCLUDE_FILES],
        key=lambda p: p.name.lower(),
    )


def mode_name(path: Path) -> str:
    return path.stem


def find_mode_files(modes: list[str]) -> list[Path]:
    candidates = {mode_name(p).lower(): p for p in list_modes()}
    mode_files: list[Path] = []

    if not modes:
        raise ValueError("No mode specified. Use --mode, --modes, or --all.")

    for mode in modes:
        key = mode.lower()
        if key == "all":
            return list_modes()
        if key.endswith(".modelfile"):
            key = Path(key).stem.lower()
        if key in candidates:
            mode_files.append(candidates[key])
            continue
        matches = [p for name, p in candidates.items() if name.startswith(key)]
        if len(matches) == 1:
            mode_files.append(matches[0])
            continue
        if matches:
            raise ValueError(
                f"Mode '{mode}' is ambiguous. Possible matches: {', '.join(mode_name(p) for p in matches)}"
            )
        raise FileNotFoundError(
            f"Mode '{mode}' not found. Available modes: {', '.join(mode_name(p) for p in list_modes())}"
        )

    unique_modes: list[Path] = []
    seen: set[Path] = set()
    for mode in mode_files:
        if mode not in seen:
            unique_modes.append(mode)
            seen.add(mode)
    return unique_modes


def assemble_modelfile(base_text: str, mode_texts: list[str]) -> str:
    closing = '"""'
    idx = base_text.rfind(closing)
    if idx == -1:
        raise ValueError("Base.Modelfile does not contain a closing SYSTEM block delimiter (\"\"\").")

    prefix = base_text[:idx].rstrip()
    suffix = base_text[idx:]
    body = "\n\n".join(text.strip() for text in mode_texts)

    return f"{prefix}\n\n{body}\n\n{suffix}"


def build(modes: list[str], output: Path) -> Path:
    if not BASE_FILE.exists():
        raise FileNotFoundError(f"Base.Modelfile not found at {BASE_FILE}")

    mode_files = find_mode_files(modes)
    if not mode_files:
        raise ValueError("No mode files found to build.")

    base_text = BASE_FILE.read_text(encoding="utf-8")
    mode_texts = [mode_file.read_text(encoding="utf-8") for mode_file in mode_files]
    full_text = assemble_modelfile(base_text, mode_texts)

    output.write_text(full_text, encoding="utf-8")
    return output


def create_ollama_model(output: Path, model_name: str, force: bool) -> int:
    cmd = ["ollama", "create", model_name, "-f", str(output)]
    if force:
        cmd.append("--force")

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout, end="")
    if result.returncode != 0:
        print(result.stderr, end="", file=sys.stderr)
    return result.returncode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a combined Ollama Modelfile from Base.Modelfile and selected mode fragments.",
    )
    parser.add_argument(
        "--mode",
        required=False,
        default="SparkleNotes",
        help="The mode fragment to append (e.g. SparkleNotes, ImmersionMode, WordBlossom).",
    )
    parser.add_argument(
        "--modes",
        nargs="+",
        help="One or more mode fragments to append, separated by spaces.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Combine all available mode fragments into a single Modelfile.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Path to write the combined Modelfile.",
    )
    parser.add_argument(
        "--create",
        action="store_true",
        help="After building the Modelfile, run ollama create to register the model.",
    )
    parser.add_argument(
        "--model-name",
        default="xiaoxi",
        help="Ollama model name to create when using --create.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Pass --force to ollama create if supported.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available mode fragments and exit.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.list:
        print("Available modes:")
        for mode_file in list_modes():
            print(f"- {mode_name(mode_file)}")
        return 0

    if args.all:
        target_modes = ["all"]
    elif args.modes:
        target_modes = args.modes
    else:
        target_modes = [args.mode]

    output_path = Path(args.output)
    mode_names = ", ".join(target_modes)
    print(f"Building Modelfile from Base.Modelfile + {mode_names}")
    build(target_modes, output_path)
    print(f"Wrote combined Modelfile to {output_path}")

    if args.create:
        code = create_ollama_model(output_path, args.model_name, args.force)
        if code != 0:
            print("ollama create failed.", file=sys.stderr)
            return code
        print(f"Ollama model '{args.model_name}' created successfully.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
