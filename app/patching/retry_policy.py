class RetryPolicy:
    """Decide whether another repair attempt should be made."""

    def __init__(self, max_attempts: int = 3):
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")

        self.max_attempts = max_attempts

    def should_retry(
        self,
        attempt_count: int,
        failure: dict | None,
    ) -> dict:
        """Return a structured retry decision."""

        if failure is None:
            return {
                "retry": False,
                "reason": "No failure information was provided.",
            }

        if attempt_count >= self.max_attempts:
            return {
                "retry": False,
                "reason": "Maximum repair attempts reached.",
            }

        if not failure.get("retryable", False):
            return {
                "retry": False,
                "reason": "The failure is not considered retryable.",
            }

        return {
            "retry": True,
            "reason": "The failure is retryable and the attempt limit has not been reached.",
        }