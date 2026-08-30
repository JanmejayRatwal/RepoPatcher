class FailureAnalyzer:
    """Classify the result of a failed repair verification."""

    def analyze(self, verification_result: dict) -> dict:
        if not verification_result:
            return {
                "category": "unknown",
                "retryable": False,
                "reason": "No verification result was provided.",
            }

        test_result = verification_result.get("test_result", {})

        status = test_result.get("status")
        exit_code = test_result.get("exit_code")
        stdout = test_result.get("stdout", "") or ""
        stderr = test_result.get("stderr", "") or ""

        combined_output = f"{stdout}\n{stderr}".lower()

        if status == "timeout":
            return {
                "category": "timeout",
                "retryable": True,
                "reason": "Test execution timed out.",
            }

        if status == "execution_error":
            return {
                "category": "execution_error",
                "retryable": False,
                "reason": "The test runner could not execute the test suite.",
            }

        if status == "repository_not_found":
            return {
                "category": "repository_error",
                "retryable": False,
                "reason": "The target repository could not be found.",
            }

        if status == "invalid_repository":
            return {
                "category": "repository_error",
                "retryable": False,
                "reason": "The target path is not a valid repository directory.",
            }

        if status == "failed" or exit_code not in (None, 0):
            return {
                "category": "test_failure",
                "retryable": True,
                "reason": "The repair was applied but the test suite still fails.",
                "output": combined_output,
            }

        return {
            "category": "unknown",
            "retryable": False,
            "reason": "The verification failure could not be classified.",
        }