import pytest

from app.patching.retry_policy import RetryPolicy


def test_retry_when_failure_is_retryable():

    policy = RetryPolicy(max_attempts=3)

    result = policy.should_retry(
        attempt_count=1,
        failure={
            "retryable": True,
            "category": "test_failure",
        },
    )

    assert result["retry"] is True


def test_stop_at_max_attempts():

    policy = RetryPolicy(max_attempts=3)

    result = policy.should_retry(
        attempt_count=3,
        failure={
            "retryable": True,
            "category": "test_failure",
        },
    )

    assert result["retry"] is False


def test_non_retryable_failure():

    policy = RetryPolicy(max_attempts=3)

    result = policy.should_retry(
        attempt_count=1,
        failure={
            "retryable": False,
            "category": "execution_error",
        },
    )

    assert result["retry"] is False


def test_missing_failure():

    policy = RetryPolicy(max_attempts=3)

    result = policy.should_retry(
        attempt_count=1,
        failure=None,
    )

    assert result["retry"] is False


def test_invalid_max_attempts():

    with pytest.raises(ValueError):
        RetryPolicy(max_attempts=0)