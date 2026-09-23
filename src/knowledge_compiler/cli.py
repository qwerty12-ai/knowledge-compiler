import argparse
from pathlib import Path
from knowledge_compiler.discovery import discover_files

def analyze(repository: str) -> None:
    path = Path(repository)

    if not path.exists():
        print(f"Error: repository does not exist: {path}")
        return

    if not path.is_dir():
        print(f"Error: repository is not a directory: {path}")
        return

    print(f"Analyzing repository: {path.resolve()}")

    files = discover_files(path)

    print(f"Discovered {len(files)} files")

    for file in files:
        print(f"{file.path.relative_to(path)}")

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

    args = parser.parse_args()

    if args.command == "analyze":
        analyze(args.repository)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()