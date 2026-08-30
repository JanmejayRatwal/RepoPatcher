import re
from pathlib import Path

from app.repository.scanner import RepositoryScanner
from app.analysis.test_runner import TestRunner
from app.retrieval.context_builder import ContextBuilder
from app.llm.analysis_service import LLMAnalysisService
from app.patching.repair_session import RepairSession


class RepairService:
    """
    Application-level orchestration for the RepoPatcher prototype.

    Connects the API layer to the existing repair pipeline.
    """

    def __init__(
        self,
        scanner=None,
        test_runner=None,
        context_builder=None,
        analysis_service=None,
        repair_session=None,
    ):
        self.scanner = (
            scanner
            if scanner is not None
            else RepositoryScanner()
        )

        self.test_runner = (
            test_runner
            if test_runner is not None
            else TestRunner()
        )

        self.context_builder = (
            context_builder
            if context_builder is not None
            else ContextBuilder()
        )

        self.analysis_service = (
            analysis_service
            if analysis_service is not None
            else LLMAnalysisService()
        )

        self.repair_session = (
            repair_session
            if repair_session is not None
            else RepairSession()
        )

    def repair(
        self,
        repository_path: str,
        user_error: str | None = None,
    ) -> dict:
        """Execute one complete RepoPatcher repair request."""

        repository = Path(repository_path).resolve()

        if not repository.exists():
            return {
                "success": False,
                "status": "invalid_repository",
                "error": "Repository path does not exist.",
            }

        if not repository.is_dir():
            return {
                "success": False,
                "status": "invalid_repository",
                "error": "Repository path must be a directory.",
            }

        # --------------------------------------------------
        # 1. Scan repository
        # --------------------------------------------------

        scan_result = self.scanner.scan(
            str(repository)
        )

        # --------------------------------------------------
        # 2. Run tests
        # --------------------------------------------------

        test_result = self.test_runner.run(
            str(repository)
        )

        # --------------------------------------------------
        # 3. Stop if tests already pass
        # --------------------------------------------------

        if test_result.get("success", False):
            return {
                "success": True,
                "status": "no_error_detected",
                "scan": scan_result,
                "tests": test_result,
                "message": "No repairable error was detected.",
            }

        # --------------------------------------------------
        # 4. Determine error information
        # --------------------------------------------------

        error_message = (
            user_error
            if user_error
            else self._extract_error_message(
                test_result
            )
        )

        location = self._extract_failure_location(
            test_result,
            repository,
        )

        if location is None:
            return {
                "success": False,
                "status": "error_location_not_found",
                "error": error_message,
                "scan": scan_result,
                "tests": test_result,
                "message": (
                    "Tests failed, but RepoPatcher could "
                    "not determine the failing file and line."
                ),
            }

        file_path, line_number = location

        # --------------------------------------------------
        # 5. Build structured context
        # --------------------------------------------------

        context = self.context_builder.build(
            repository_path=str(repository),
            file_path=str(file_path),
            line_number=line_number,
            error_message=error_message,
        )

        if not context.get("success", False):
            return {
                "success": False,
                "status": "context_build_failed",
                "error": context.get(
                    "error",
                    "Failed to build repair context.",
                ),
                "scan": scan_result,
                "tests": test_result,
                "context": context,
            }

        # --------------------------------------------------
        # 6. Analyze context with LLM
        # --------------------------------------------------

        analysis_result = self.analysis_service.analyze(
            context
        )

        if not analysis_result.get("success", False):
            return {
                "success": False,
                "status": "analysis_failed",
                "error": analysis_result.get(
                    "error",
                    "LLM analysis failed.",
                ),
                "scan": scan_result,
                "tests": test_result,
                "context": context,
                "analysis": analysis_result,
            }

        # --------------------------------------------------
        # 7. Execute repair session
        # --------------------------------------------------

        repair_result = self.repair_session.run(
            repository_path=str(repository),
            context=context,
            analysis=analysis_result,
        )

        return {
            "success": repair_result["success"],
            "status": repair_result["status"],
            "error": error_message,
            "location": {
                "file": str(file_path),
                "line": line_number,
            },
            "scan": scan_result,
            "tests": test_result,
            "context": context,
            "analysis": analysis_result,
            "repair": repair_result,
        }

    @staticmethod
    def _extract_error_message(test_result: dict) -> str:
        """Extract the most useful error information."""

        stdout = test_result.get("stdout", "")
        stderr = test_result.get("stderr", "")

        if stderr:
            return stderr.strip()

        if stdout:
            return stdout.strip()

        return "Unknown test failure."

    @staticmethod
    def _extract_failure_location(
        test_result: dict,
        repository: Path,
    ):
        """
        Extract a file and line number from pytest output.

        Example:

            test/test_calculator.py:5: AssertionError
        """

        output = (
            test_result.get("stdout", "")
            + "\n"
            + test_result.get("stderr", "")
        )

        pattern = re.compile(
            r"(?P<file>[^\s:]+\.py):(?P<line>\d+)"
        )

        matches = pattern.findall(output)

        if not matches:
            return None

        for relative_file, line in matches:

            candidate = (
                repository / relative_file
            ).resolve()

            try:
                candidate.relative_to(repository)
            except ValueError:
                continue

            if candidate.exists() and candidate.is_file():
                return candidate, int(line)

        return None