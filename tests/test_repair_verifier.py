from app.patching.repair_verifier import RepairVerifier


class FakeTestRunner:

    def __init__(self, result):
        self.result = result

    def run(self, repository_path):
        return self.result


def test_repair_is_verified():

    runner = FakeTestRunner(
        {
            "success": True,
            "status": "passed",
            "exit_code": 0,
            "stdout": "1 passed",
            "stderr": "",
        }
    )

    verifier = RepairVerifier(
        test_runner=runner
    )

    result = verifier.verify("/fake/repository")

    assert result["success"] is True
    assert result["verified"] is True
    assert result["status"] == "repair_verified"


def test_repair_fails_verification():

    runner = FakeTestRunner(
        {
            "success": False,
            "status": "failed",
            "exit_code": 1,
            "stdout": "",
            "stderr": "1 failed",
        }
    )

    verifier = RepairVerifier(
        test_runner=runner
    )

    result = verifier.verify("/fake/repository")

    assert result["success"] is True
    assert result["verified"] is False
    assert result["status"] == "repair_failed"


def test_verifier_preserves_test_result():

    test_result = {
        "success": False,
        "status": "timeout",
        "exit_code": None,
        "stdout": "",
        "stderr": "Test execution timed out.",
    }

    runner = FakeTestRunner(test_result)

    verifier = RepairVerifier(
        test_runner=runner
    )

    result = verifier.verify("/fake/repository")

    assert result["success"] is True
    assert result["verified"] is False
    assert result["test_result"] == test_result