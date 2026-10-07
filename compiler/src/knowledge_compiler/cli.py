import argparse
import json

from knowledge_compiler.pipeline import compile_repository


def print_human_result(result) -> None:
    print(f"Analyzing repository: {result.repository}")
    print(f"Discovered {result.files_discovered} files")

    for item in result.evidence:
        print(f"Evidence: {item.description}")

    print(f"Generated {len(result.claims)} claims")

    for claim in result.claims:
        print(f"Claim: {claim.statement}")
        print(f"Status: {claim.status}")
        print(f"Confidence: {claim.confidence:.2f}")

        for evidence_id in claim.evidence_ids:
            print(f"    Evidence: {evidence_id}")

    if result.errors:
        print("\nErrors:")
        for error in result.errors:
            print(f"    - {error}")


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

    analyze_parser.add_argument(
        "--json",
        action="store_true",
        help="Output the analysis result as JSON",
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
            file.write(result.to_json())
        print(f"Analysis written to {args.output}")
        return

    if args.json:
        print(result.to_json())
        return

    print_human_result(result)


if __name__ == "__main__":
    main()