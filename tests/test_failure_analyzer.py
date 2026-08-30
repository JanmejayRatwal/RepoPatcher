from app.analysis.failure_analyzer import FailureAnalyzer


def test_test_failure_is_retryable():

    analyzer = FailureAnalyzer()

    result = analyzer.analyze(
        {
            "test_result": {
                "status": "failed",
                "exit_code": 1,
                "stdout": "1 failed",
                "stderr": "",
            }
        }
    )

    assert result["category"] == "test_failure"
    assert result["retryable"] is True


def test_timeout_is_retryable():

    analyzer = FailureAnalyzer()

    result = analyzer.analyze(
        {
            "test_result": {
                "status": "timeout",
                "exit_code": None,
                "stdout": "",
                "stderr": "",
            }
        }
    )

    assert result["category"] == "timeout"
    assert result["retryable"] is True


def test_execution_error_is_not_retryable():

    analyzer = FailureAnalyzer()

    result = analyzer.analyze(
        {
            "test_result": {
                "status": "execution_error",
                "exit_code": None,
                "stdout": "",
                "stderr": "Permission denied",
            }
        }
    )

    assert result["category"] == "execution_error"
    assert result["retryable"] is False


def test_missing_verification_result():

    analyzer = FailureAnalyzer()

    result = analyzer.analyze(None)

    assert result["category"] == "unknown"
    assert result["retryable"] is False