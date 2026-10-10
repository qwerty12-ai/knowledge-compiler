import argparse
import json
import os
import sys

from knowledge_compiler.pipeline import compile_repository
from .terminal_logo import render_terminal_logo

class TerminalStyle:
    AMBER = "\033[38;5;214m"
    GRAPHITE = "\033[38;5;242m"
    MUTED = "\033[38;5;245m"
    RESET = "\033[0m"

    @staticmethod
    def colors_enabled() -> bool:
        return (
            sys.stdout.isatty() and "NO_COLOR" not in os.environ
        )

STATUS_SYMBOLS = {
    "VERIFIED": "[+]",
    "SUPPORTED": "[~]",
    "WEAKLY_SUPPORTED": "[!]",
    "UNKNOWN": "[?]",
    "CONTRADICTED": "[x]",
    "STALE": "[~]",
}


def serialize_result(result, compact: bool = False) -> str:
    if not compact:
        return result.to_json()

    payload = result.to_dict()

    for evidence in payload["evidence"]:
        evidence["content"] = None

    return json.dumps(payload, indent=2)

def print_banner() -> None:
    use_color = TerminalStyle.colors_enabled()

    def paint(text: str, color: str) -> str:
        if not use_color:
            return text
        return f"{color}{text}{TerminalStyle.RESET}"

    if not use_color:
        print()
        print("KNOWLEDGE")
        print("COMPILER")
        print("Evidence-backed repository analysis")
        print()
        return

    logo_lines = render_terminal_logo(width=32)

    wordmark = [
        "",
        "",
        paint("KNOWLEDGE", TerminalStyle.GRAPHITE),
        paint("COMPILER", TerminalStyle.AMBER),
        "",
        paint("Evidence-backed", TerminalStyle.MUTED),
        paint("repository analysis", TerminalStyle.MUTED),
    ]

    print()

    for index, logo_line in enumerate(logo_lines):
        text = wordmark[index] if index < len(wordmark) else ""
        print(f"  {logo_line}  {text}")

    print()

def print_human_result(result) -> None:
    use_color = TerminalStyle.colors_enabled()

    def paint(text: str, color: str) -> str:
        if not use_color:
            return text
        return f"{color}{text}{TerminalStyle.RESET}"

    def excerpt(content: str | None, limit: int = 180) -> str | None:
        if not content or not content.strip():
            return None

        normalized = " ".join(content.split())
        if len(normalized) > limit:
            return normalized[: limit - 3].rstrip() + "..."
        return normalized

    repository_name = result.repository.rstrip("/").split("/")[-1]
    evidence_by_id = {item.id: item for item in result.evidence}
    previewed_evidence_ids: set[str] = set()

    print()
    print(paint("KNOWLEDGE COMPILER", TerminalStyle.AMBER))
    print("=" * 64)
    print(f"Repository : {repository_name or result.repository}")
    print(f"Location   : {result.repository}")
    print(f"Files      : {result.files_discovered}")
    print(f"Mode       : {'AI-assisted' if result.with_ai else 'Deterministic'}")
    print()

    print(paint("ANALYSIS SUMMARY", TerminalStyle.GRAPHITE))
    print("-" * 64)
    print(f"Claims generated : {len(result.claims)}")
    print(f"Evidence items   : {len(result.evidence)}")
    print(f"Errors           : {len(result.errors)}")

    if result.claims:
        print()
        print(paint("CLAIMS & SUPPORTING EVIDENCE", TerminalStyle.GRAPHITE))
        print("-" * 64)

        for claim in result.claims:
            status = getattr(claim.status, "value", str(claim.status))
            symbol = STATUS_SYMBOLS.get(status, "[ ]")

            status_color = (
                TerminalStyle.AMBER
                if status in {"VERIFIED", "SUPPORTED"}
                else TerminalStyle.MUTED
            )

            print(paint(f"{symbol} {claim.id}  {status}", status_color))
            print(f"  {claim.statement}")
            print(f"  Confidence: {claim.confidence:.0%}")

            if claim.evidence_ids:
                displayed_evidence = claim.evidence_ids[:3]
                print(
                    f"  Supporting evidence "
                    f"({len(claim.evidence_ids)} linked item(s)):"
                )

                for evidence_id in displayed_evidence:
                    item = evidence_by_id.get(evidence_id)

                    if item is None:
                        print(f"    - {evidence_id}: details unavailable")
                        continue

                    location = item.source
                    if item.line_start is not None:
                        location += f":{item.line_start}"
                        if (
                            item.line_end is not None
                            and item.line_end != item.line_start
                        ):
                            location += f"-{item.line_end}"

                    kind = item.kind.replace("_", " ")
                    print(f"    [{kind}] {location}")
                    print(f"      {item.description}")

                    preview = excerpt(item.content)
                    if preview and evidence_id not in previewed_evidence_ids:
                        print(f"      Preview: {preview}")
                        previewed_evidence_ids.add(evidence_id)

                remaining = len(claim.evidence_ids) - len(displayed_evidence)
                if remaining > 0:
                    print(f"    ... and {remaining} more linked item(s)")

            else:
                print("  Supporting evidence: none linked")

            print()

    if result.errors:
        print(paint("INVESTIGATION ERRORS", TerminalStyle.MUTED))
        print("-" * 64)
        for error in result.errors:
            print(f"  - {error}")
        print()

    print("=" * 64)
    if result.errors:
        print("Analysis completed with errors.")
    else:
        print("Initial investigation complete.")

    print()
    print(paint("READY TO INVESTIGATE FURTHER?", TerminalStyle.AMBER))
    print(
        "Create a new analysis of this same repository in the Knowledge "
        "Compiler forensic workstation."
    )
    print(
        "Explore claims and their supporting evidence in greater depth, "
        "then consult an AI assistant if needed."
    )
    print(
        "Note: this CLI analysis does not automatically appear in the "
        "workstation."
    )
    print()

def analyze(
    repository: str,
    with_ai: bool = False,
    limit: int | None = None,
):
    return compile_repository(
        repository=repository,
        with_ai=with_ai,
        limit=limit,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="knowledge-compiler",
        description="Analyze a software repository and build engineering knowledge",
    )

    subparsers = parser.add_subparsers(dest="command")

    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze a repository",
    )

    analyze_parser.add_argument(
        "repository",
        help="Path to the repository to analyze",
    )

    analyze_parser.add_argument(
        "--with-ai",
        action="store_true",
        help="Enable AI investigation using the local Ollama model",
    )

    analyze_parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of investigation units to analyze with AI",
    )

    output_format = analyze_parser.add_mutually_exclusive_group()

    output_format.add_argument(
        "--json",
        action="store_true",
        help="Output the full analysis result as JSON",
    )

    output_format.add_argument(
        "--compact-json",
        action="store_true",
        help="Output JSON without embedded source content",
    )

    analyze_parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Write the analysis result to a JSON file",
    )

    args = parser.parse_args()

    if args.command != "analyze":
        parser.print_help()
        return

    try:
        result = compile_repository(
            repository=args.repository,
            with_ai=args.with_ai,
            limit=args.limit,
        )
    except ValueError as error:
        parser.error(str(error))
        return

    if args.output:
        with open(args.output, "w", encoding="utf-8") as file:
            file.write(
                serialize_result(
                    result,
                    compact=args.compact_json,
                )
            )

        print(f"Analysis written to {args.output}")
        return

    if args.json or args.compact_json:
        print(
            serialize_result(
                result,
                compact=args.compact_json,
            )
        )
        return

    print_banner()
    print_human_result(result)


if __name__ == "__main__":
    main()