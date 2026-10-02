import argparse
from pathlib import Path
from knowledge_compiler.claims import generate_claims
from knowledge_compiler.context import build_repository_context
from knowledge_compiler.investigation import build_investigation_units
from knowledge_compiler.investigator import investigate
from knowledge_compiler.observation_evidence import (convert_observations_to_evidence)

def analyze(repository: str, with_ai: bool = False) -> None:
    path = Path(repository)

    if not path.exists():
        print(f"Error: repository does not exist: {path}")
        return

    if not path.is_dir():
        print(f"Error: repository is not a directory: {path}")
        return

    print(f"Analyzing repository: {path.resolve()}")

    context = build_repository_context(path)

    print(f"Discovered {len(context.files)} files")

    for file in context.files:
        print(f"{file.path}")   

    for item in context.evidence:
        print(f"Evidence: {item.description}")

    all_evidence = list(context.evidence)

    if with_ai:
        units = build_investigation_units(context)
        print(f"Created {len(units)} investigation units")

        for unit in units:
            result = investigate(unit)
            observation_evidence = convert_observations_to_evidence(result)
            all_evidence.extend(observation_evidence)

    claims = generate_claims(all_evidence)

    print(f"Generated {len(claims)} claims")

    for claim in claims:
        print(f"Claim: {claim.statement}")
        print(f"Status: {claim.status}")
        print(f"Confidence: {claim.confidence:.2f}")

        for item in claim.evidence:
            print(f"    Source: {item.source}")
            print(f"    Evidence type: {item.kind}")

            if item.line_start is not None:
                print(f"    Lines: {item.line_start} - {item.line_end}")

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="knowledge-compiler",
        description="Analyze a software repository and build engineering knowledge"
    )

    subparsers = parser.add_subparsers(dest="command")

    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze a repository"
    )

    analyze_parser.add_argument(
        "repository",
        help="Path to the repository to analyze"
    )

    analyze_parser.add_argument(
        "--with-ai",
        action="store_true",
        help="Enable AI investigation using the local Ollama model"
    )

    args = parser.parse_args()

    if args.command == "analyze":
        analyze(args.repository,with_ai=args.with_ai)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()