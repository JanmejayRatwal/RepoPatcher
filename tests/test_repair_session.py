from app.patching.repair_session import RepairSession


class SuccessfulWorkflow:

    def __init__(self):
        self.calls = 0

    def run(self, repository_path, context, analysis):

        self.calls += 1

        return {
            "success": True,
            "stage": "verification",
            "verification": {
                "verified": True,
            },
        }


class RetryThenSuccessWorkflow:

    def __init__(self):
        self.calls = 0

    def run(self, repository_path, context, analysis):

        self.calls += 1

        if self.calls == 1:
            return {
                "success": False,
                "stage": "verification",
                "failure": {
                    "category": "test_failure",
                    "retryable": True,
                },
                "retry_decision": {
                    "retry": True,
                    "reason": "Retry allowed.",
                },
            }

        return {
            "success": True,
            "stage": "verification",
            "verification": {
                "verified": True,
            },
        }


class AlwaysFailWorkflow:

    def __init__(self):
        self.calls = 0

    def run(self, repository_path, context, analysis):

        self.calls += 1

        return {
            "success": False,
            "stage": "verification",
            "failure": {
                "category": "test_failure",
                "retryable": True,
            },
            "retry_decision": {
                "retry": True,
                "reason": "Retry allowed.",
            },
        }


def test_successful_repair_requires_one_attempt():

    workflow = SuccessfulWorkflow()

    session = RepairSession(
        repair_workflow=workflow,
        max_attempts=3,
    )

    result = session.run(
        "/fake/repository",
        {},
        {},
    )

    assert result["success"] is True
    assert result["status"] == "repair_completed"
    assert result["attempt_count"] == 1
    assert workflow.calls == 1


def test_retry_then_success():

    workflow = RetryThenSuccessWorkflow()

    session = RepairSession(
        repair_workflow=workflow,
        max_attempts=3,
    )

    result = session.run(
        "/fake/repository",
        {},
        {},
    )

    assert result["success"] is True
    assert result["attempt_count"] == 2
    assert len(result["attempts"]) == 2
    assert workflow.calls == 2


def test_max_attempts_reached():

    workflow = AlwaysFailWorkflow()

    session = RepairSession(
        repair_workflow=workflow,
        max_attempts=3,
    )

    result = session.run(
        "/fake/repository",
        {},
        {},
    )

    assert result["success"] is False
    assert result["status"] == "maximum_attempts_reached"
    assert result["attempt_count"] == 3
    assert len(result["attempts"]) == 3
    assert workflow.calls == 3


def test_invalid_max_attempts():

    workflow = SuccessfulWorkflow()

    try:
        RepairSession(
            repair_workflow=workflow,
            max_attempts=0,
        )
        assert False
    except ValueError:
        pass