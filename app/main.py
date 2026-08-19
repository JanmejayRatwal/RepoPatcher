import sys

from app.analysis.test_runner import TestRunner
from app.repository.scanner import RepositoryScanner


def print_scan_result(result: dict):
    """Print repository scanning results."""

    print("\nRepoMedic - Repository Scan")
    print("=" * 40)

    print(f"Repository: {result['repository']}")
    print(f"Python files scanned: {result['files_scanned']}")
    print(f"Syntax errors found: {result['errors_found']}")

    print("\nFile Results")
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


def print_test_result(result: dict):
    """Print test execution results."""

    print("\nTest Execution")
    print("=" * 40)

    print(f"Status: {result['status']}")
    print(f"Exit code: {result['exit_code']}")

    if result["stdout"]:
        print("\nSTDOUT")
        print("-" * 40)
        print(result["stdout"])

    if result["stderr"]:
        print("\nSTDERR")
        print("-" * 40)
        print(result["stderr"])


def main():
    if len(sys.argv) != 2:
        print(
            "Usage: python -m app.main <repository_path>"
        )
        sys.exit(1)

    repository_path = sys.argv[1]

    scanner = RepositoryScanner()

    try:
        scan_result = scanner.scan(repository_path)

    except (FileNotFoundError, NotADirectoryError) as error:
        print(f"Error: {error}")
        sys.exit(1)

    print_scan_result(scan_result)

    runner = TestRunner()
    test_result = runner.run(repository_path)

    print_test_result(test_result)

    if (
        scan_result["errors_found"] > 0
        or not test_result["success"]
    ):
        sys.exit(1)


if __name__ == "__main__":
    main()