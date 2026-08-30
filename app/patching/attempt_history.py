from datetime import datetime, timezone


class RepairAttemptHistory:
    """Store and retrieve repair attempts for a single repair workflow."""

    def __init__(self):
        self._attempts = []

    def record(
        self,
        repair: dict,
        validation: dict | None = None,
        application: dict | None = None,
        verification: dict | None = None,
        failure: dict | None = None,
        provider: str | None = None,
        model: str | None = None,
    ) -> dict:

        attempt = {
            "attempt_number": len(self._attempts) + 1,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "provider": provider,
            "model": model,
            "repair": repair,
            "validation": validation,
            "application": application,
            "verification": verification,
            "failure": failure,
        }

        self._attempts.append(attempt)

        return attempt

    def get_all(self) -> list[dict]:
        """Return all recorded attempts."""
        return list(self._attempts)

    def get_latest(self) -> dict | None:
        """Return the most recent attempt."""
        if not self._attempts:
            return None

        return self._attempts[-1]

    def count(self) -> int:
        """Return the number of recorded attempts."""
        return len(self._attempts)

    def clear(self) -> None:
        """Clear all recorded attempts."""
        self._attempts.clear()