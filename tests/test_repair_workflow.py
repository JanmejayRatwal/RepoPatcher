from app.patching.repair_workflow import RepairWorkflow


class FakeRepairGenerator:

    def generate(self, context, analysis):
        return {
            "success": True,
            "repair": {
                "file": "calculator.py",
                "target": "add",
                "change_type": "replace",
                "original": "return a - b",
                "replacement": "return a + b",
                "reason": "Fix addition logic.",
            },
        }


class FakePatchValidator:

    def validate(self, repository_path, repair):
        return {
            "valid": True,
            "file": "calculator.py",
            "occurrences": 1,
        }


class FakePatchApplier:

    def apply(self, repository_path, repair):
        return {
            "success": True,
            "file": "calculator.py",
            "occurrences": 1,
        }


class FakeRepairVerifier:

    def verify(self, repository_path):
        return {
            "success": True,
            "verified": True,
            "status": "repair_verified",
            "test_result": {
                "success": True,
                "status": "passed",
                "exit_code": 0,
                "stdout": "1 passed",
                "stderr": "",
            },
        }


def test_complete_repair_workflow():

    workflow = RepairWorkflow(
        repair_generator=FakeRepairGenerator(),
        patch_validator=FakePatchValidator(),
        patch_applier=FakePatchApplier(),
        repair_verifier=FakeRepairVerifier(),
    )

    result = workflow.run(
        repository_path="/fake/repository",
        context={"error": "calculator failure"},
        analysis={
            "analysis": "Wrong operator.",
        },
    )

    assert result["success"] is True
    assert result["stage"] == "verification"

    assert result["repair"]["replacement"] == "return a + b"

    assert result["validation"]["valid"] is True

    assert result["application"]["success"] is True

    assert result["verification"]["verified"] is True


def test_workflow_stops_when_generation_fails():

    class FailedGenerator:

        def generate(self, context, analysis):
            return {
                "success": False,
                "error": "LLM unavailable",
            }

    workflow = RepairWorkflow(
        repair_generator=FailedGenerator(),
        patch_validator=FakePatchValidator(),
        patch_applier=FakePatchApplier(),
        repair_verifier=FakeRepairVerifier(),
    )

    result = workflow.run(
        "/fake/repository",
        {},
        {},
    )

    assert result["success"] is False
    assert result["stage"] == "repair_generation"


def test_workflow_stops_when_validation_fails():

    class FailedValidator:

        def validate(self, repository_path, repair):
            return {
                "valid": False,
                "error": "Invalid patch",
            }

    workflow = RepairWorkflow(
        repair_generator=FakeRepairGenerator(),
        patch_validator=FailedValidator(),
        patch_applier=FakePatchApplier(),
        repair_verifier=FakeRepairVerifier(),
    )

    result = workflow.run(
        "/fake/repository",
        {},
        {},
    )

    assert result["success"] is False
    assert result["stage"] == "patch_validation"