from app.analysis.test_runner import TestRunner


class RepairVerifier:
    """Verify whether an applied repair makes the repository pass its tests."""

    def __init__(self, test_runner=None):
        self.test_runner = (
            test_runner
            if test_runner is not None
            else TestRunner()
        )

    def verify(self, repository_path: str) -> dict:
        """Run the repository test suite and return verification results."""

        result = self.test_runner.run(repository_path)

        if result["success"]:
            return {
                "success": True,
                "verified": True,
                "status": "repair_verified",
                "test_result": result,
            }

        return {
            "success": True,
            "verified": False,
            "status": "repair_failed",
            "test_result": result,
        }