import sys

from app.repository.scanner import RepositoryScanner


def print_result(result: dict):
    """Print repository scan results."""

    print("\nRepoMedic - Repository Scan")
    print("=" * 40)

    print(f"Repository: {result['repository']}")
    print(f"Python files scanned: {result['files_scanned']}")
    print(f"Errors found: {result['errors_found']}")

    print("\nResults")
    print("-" * 40)

    for file_result in result["results"]:
        if file_result["success"]:
            print(f"[PASS] {file_result['file']}")
        else:
            print(
                f"[ERROR] {file_result['file']} "
                f"- {file_result['error_type']}"
            )

            print(
                f"        {file_result['message']}"
            )

            if file_result.get("line"):
                print(
                    f"        Line: {file_result['line']}"
                )


def main():
    if len(sys.argv) != 2:
        print(
            "Usage: python -m app.main <repository_path>"
        )
        sys.exit(1)

    repository_path = sys.argv[1]

    scanner = RepositoryScanner()

    try:
        result = scanner.scan(repository_path)

    except (FileNotFoundError, NotADirectoryError) as error:
        print(f"Error: {error}")
        sys.exit(1)

    print_result(result)

    if result["errors_found"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()