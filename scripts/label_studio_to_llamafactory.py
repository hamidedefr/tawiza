#!/usr/bin/env python3
"""
Convert Label Studio exports to LLaMA-Factory format.
Supports both Alpaca (instruction/input/output) and ShareGPT (conversations) formats.
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def convert_label_studio_to_alpaca(annotations: list[dict[str, Any]]) -> list[dict[str, str]]:
    """
    Convert Label Studio annotations to Alpaca format for LLaMA-Factory.

    Expected Label Studio format (from TextArea annotations):
    {
        "id": 1,
        "annotations": [{
            "result": [
                {"from_name": "instruction", "value": {"text": ["..."]}, ...},
                {"from_name": "input", "value": {"text": ["..."]}, ...},
                {"from_name": "output", "value": {"text": ["..."]}, ...}
            ]
        }]
    }

    Output Alpaca format:
    {"instruction": "...", "input": "...", "output": "..."}
    """
    results = []

    for task in annotations:
        task_annotations = task.get("annotations", [])
        if not task_annotations:
            continue

        # Get the first (or most recent) annotation
        annotation = task_annotations[0]
        result = annotation.get("result", [])

        entry = {"instruction": "", "input": "", "output": ""}

        for item in result:
            field_name = item.get("from_name", "")
            value = item.get("value", {})

            # Handle TextArea results
            if "text" in value:
                text = value["text"]
                if isinstance(text, list):
                    text = text[0] if text else ""

                if field_name == "instruction":
                    entry["instruction"] = text.strip()
                elif field_name == "input":
                    entry["input"] = text.strip()
                elif field_name == "output":
                    entry["output"] = text.strip()

        # Only add if we have at least instruction and output
        if entry["instruction"] and entry["output"]:
            results.append(entry)

    return results


def convert_label_studio_to_sharegpt(annotations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Convert Label Studio annotations to ShareGPT format for multi-turn conversations.

    Output ShareGPT format:
    {"conversations": [
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."}
    ]}
    """
    results = []

    for task in annotations:
        alpaca_entries = convert_label_studio_to_alpaca([task])

        for entry in alpaca_entries:
            conversation = {"conversations": []}

            # Add instruction as user message
            user_content = entry["instruction"]
            if entry["input"]:
                user_content += f"\n\nContext:\n{entry['input']}"

            conversation["conversations"].append({"role": "user", "content": user_content})

            # Add output as assistant message
            conversation["conversations"].append({"role": "assistant", "content": entry["output"]})

            results.append(conversation)

    return results


def convert_jsonl_to_alpaca(input_path: Path) -> list[dict[str, str]]:
    """Convert existing JSONL (already in Alpaca format) to clean format."""
    results = []

    with open(input_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)

                # Standard Alpaca fields
                entry = {
                    "instruction": data.get("instruction", ""),
                    "input": data.get("input", ""),
                    "output": data.get("output", ""),
                }

                if entry["instruction"] and entry["output"]:
                    results.append(entry)
            except json.JSONDecodeError as e:
                print(f"Warning: Skipping invalid JSON line: {e}")
                continue

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Convert Label Studio exports to LLaMA-Factory format"
    )
    parser.add_argument("input", type=Path, help="Input file (Label Studio JSON export or JSONL)")
    parser.add_argument(
        "output", type=Path, help="Output file (JSONL for Alpaca, JSON for ShareGPT)"
    )
    parser.add_argument(
        "--format",
        choices=["alpaca", "sharegpt"],
        default="alpaca",
        help="Output format (default: alpaca)",
    )
    parser.add_argument(
        "--source",
        choices=["label_studio", "jsonl"],
        default="label_studio",
        help="Input source format (default: label_studio)",
    )

    args = parser.parse_args()

    # Read input
    print(f"Reading from {args.input}...")

    if args.source == "label_studio":
        with open(args.input, encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            data = [data]

        if args.format == "alpaca":
            results = convert_label_studio_to_alpaca(data)
        else:
            results = convert_label_studio_to_sharegpt(data)
    else:
        # Already JSONL
        results = convert_jsonl_to_alpaca(args.input)
        if args.format == "sharegpt":
            # Convert Alpaca to ShareGPT
            temp_results = []
            for entry in results:
                temp_results.append(
                    {
                        "conversations": [
                            {
                                "role": "user",
                                "content": entry["instruction"]
                                + (f"\n\n{entry['input']}" if entry["input"] else ""),
                            },
                            {"role": "assistant", "content": entry["output"]},
                        ]
                    }
                )
            results = temp_results

    # Write output
    print(f"Writing {len(results)} examples to {args.output}...")

    with open(args.output, "w", encoding="utf-8") as f:
        if args.format == "alpaca":
            # JSONL format
            for entry in results:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        else:
            # JSON format for ShareGPT
            json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"Done! Converted {len(results)} examples.")


if __name__ == "__main__":
    main()
