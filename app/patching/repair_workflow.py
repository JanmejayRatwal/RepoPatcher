from app.llm.repair_generator import RepairGenerator
from app.patching.patch_validator import PatchValidator
from app.patching.patch_applier import PatchApplier
from app.patching.repair_verifier import RepairVerifier
from app.patching.attempt_history import RepairAttemptHistory


class RepairWorkflow:
    """Coordinate repair generation, validation, application and verification."""

    def __init__(
        self,
        repair_generator=None,
        patch_validator=None,
        patch_applier=None,
        repair_verifier=None,
    ):
        self.repair_generator = (
            repair_generator
            if repair_generator is not None
            else RepairGenerator()
        )

        self.patch_validator = (
            patch_validator
            if patch_validator is not None
            else PatchValidator()
        )

        self.patch_applier = (
            patch_applier
            if patch_applier is not None
            else PatchApplier()
        )

        self.repair_verifier = (
            repair_verifier
            if repair_verifier is not None
            else RepairVerifier()
        )

    def run(
        self,
        repository_path: str,
        context: dict,
        analysis: dict,
    ) -> dict:
        """Execute the complete repair workflow."""

        history = RepairAttemptHistory()

        # --------------------------------------------------
        # 1. Generate repair
        # --------------------------------------------------

        generation = self.repair_generator.generate(
            context,
            analysis,
        )

        if not generation["success"]:
            attempt = history.record(
                repair={},
                failure={
                    "category": "repair_generation",
                    "error": generation["error"],
                },
            )

            return {
                "success": False,
                "stage": "repair_generation",
                "error": generation["error"],
                "attempt": attempt,
                "history": history.get_all(),
            }

        repair = generation["repair"]

        # --------------------------------------------------
        # 2. Validate repair
        # --------------------------------------------------

        validation = self.patch_validator.validate(
            repository_path,
            repair,
        )

        if not validation["valid"]:
            attempt = history.record(
                repair=repair,
                validation=validation,
                failure={
                    "category": "patch_validation",
                    "error": validation["error"],
                },
            )

            return {
                "success": False,
                "stage": "patch_validation",
                "error": validation["error"],
                "repair": repair,
                "attempt": attempt,
                "history": history.get_all(),
            }

        # --------------------------------------------------
        # 3. Apply repair
        # --------------------------------------------------

        application = self.patch_applier.apply(
            repository_path,
            repair,
        )

        if not application["success"]:
            attempt = history.record(
                repair=repair,
                validation=validation,
                application=application,
                failure={
                    "category": "patch_application",
                    "error": application["error"],
                },
            )

            return {
                "success": False,
                "stage": "patch_application",
                "error": application["error"],
                "repair": repair,
                "attempt": attempt,
                "history": history.get_all(),
            }

        # --------------------------------------------------
        # 4. Verify repair
        # --------------------------------------------------

        verification = self.repair_verifier.verify(
            repository_path
        )

        # --------------------------------------------------
        # 5. Record attempt
        # --------------------------------------------------

        attempt = history.record(
            repair=repair,
            validation=validation,
            application=application,
            verification=verification,
        )

        # --------------------------------------------------
        # 6. Return workflow result
        # --------------------------------------------------

        return {
            "success": verification.get("verified", False),
            "stage": "verification",
            "repair": repair,
            "validation": validation,
            "application": application,
            "verification": verification,
            "attempt": attempt,
            "history": history.get_all(),
        }