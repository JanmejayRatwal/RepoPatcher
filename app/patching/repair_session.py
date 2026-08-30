from app.patching.repair_workflow import RepairWorkflow
from app.patching.attempt_history import RepairAttemptHistory


class RepairSession:
    """Manage multiple repair attempts for a single repair task."""

    def __init__(
        self,
        repair_workflow=None,
        max_attempts=3,
    ):
        self.repair_workflow = (
            repair_workflow
            if repair_workflow is not None
            else RepairWorkflow()
        )

        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")

        self.max_attempts = max_attempts

    def run(
        self,
        repository_path: str,
        context: dict,
        analysis: dict,
    ) -> dict:
        """Run repair attempts until success or the limit is reached."""

        attempts = []

        # One shared history for the entire repair session.
        history = RepairAttemptHistory()

        # Inject the session-level history into the workflow.
        if hasattr(self.repair_workflow, "attempt_history"):
            self.repair_workflow.attempt_history = history

        for attempt_number in range(1, self.max_attempts + 1):

            result = self.repair_workflow.run(
                repository_path,
                context,
                analysis,
            )

            attempts.append(result)

            # ------------------------------------------
            # Repair succeeded
            # ------------------------------------------

            if result["success"]:
                return {
                    "success": True,
                    "status": "repair_completed",
                    "attempt_count": attempt_number,
                    "attempts": attempts,
                    "history": history.get_all(),
                    "final_result": result,
                }

            # ------------------------------------------
            # No retry decision
            # ------------------------------------------

            retry_decision = result.get("retry_decision")

            if not retry_decision:
                return {
                    "success": False,
                    "status": "repair_stopped",
                    "attempt_count": attempt_number,
                    "attempts": attempts,
                    "history": history.get_all(),
                    "final_result": result,
                }

            # ------------------------------------------
            # Retry not allowed
            # ------------------------------------------

            if not retry_decision.get("retry", False):
                return {
                    "success": False,
                    "status": "repair_stopped",
                    "attempt_count": attempt_number,
                    "attempts": attempts,
                    "history": history.get_all(),
                    "final_result": result,
                }

        # ----------------------------------------------
        # Maximum attempts reached
        # ----------------------------------------------

        return {
            "success": False,
            "status": "maximum_attempts_reached",
            "attempt_count": self.max_attempts,
            "attempts": attempts,
            "history": history.get_all(),
            "final_result": attempts[-1],
        }