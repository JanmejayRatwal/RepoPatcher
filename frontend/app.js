const API_URL = "http://127.0.0.1:8000/api/repair";


function setStep(step, state) {
    const element = document.getElementById(`step-${step}`);

    if (!element) {
        return;
    }

    element.classList.remove("active", "complete", "failed");

    if (state === "active") {
        element.classList.add("active");
        element.textContent = "◐ " + element.textContent.substring(2);
    }

    if (state === "complete") {
        element.classList.add("complete");
        element.textContent = "✓ " + element.textContent.substring(2);
    }

    if (state === "failed") {
        element.classList.add("failed");
        element.textContent = "✗ " + element.textContent.substring(2);
    }
}


function resetPipeline() {
    const steps = ["scan", "test", "analysis", "repair", "verify"];

    steps.forEach(step => {
        const element = document.getElementById(`step-${step}`);

        element.classList.remove(
            "active",
            "complete",
            "failed"
        );

        const names = {
            scan: "Repository Scan",
            test: "Test Execution",
            analysis: "LLM Analysis",
            repair: "Patch Generation",
            verify: "Verification"
        };

        element.textContent = "○ " + names[step];
    });
}


async function repairRepository() {

    const repositoryPath =
        document.getElementById("repositoryPath").value.trim();

    const button =
        document.getElementById("repairButton");

    const status =
        document.getElementById("status");

    if (!repositoryPath) {
        status.textContent = "Please enter a repository path.";
        return;
    }

    button.disabled = true;

    resetPipeline();

    document
        .getElementById("failureCard")
        .classList.add("hidden");

    document
        .getElementById("analysisCard")
        .classList.add("hidden");

    document
        .getElementById("repairCard")
        .classList.add("hidden");

    document
        .getElementById("resultCard")
        .classList.add("hidden");

    status.textContent = "Repairing repository...";

    setStep("scan", "active");

    try {

        const response = await fetch(
            API_URL,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    repository_path: repositoryPath
                })
            }
        );

        setStep("scan", "complete");
        setStep("test", "complete");

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(
                data.error ||
                data.message ||
                "Repair failed."
            );
        }

        displayFailure(data);

        if (data.analysis) {
            setStep("analysis", "complete");
            displayAnalysis(data.analysis);
        }

        if (data.repair) {
            setStep("repair", "complete");
            displayRepair(data.repair);
        }

        if (
            data.repair &&
            data.repair.final_result &&
            data.repair.final_result.success
        ) {
            setStep("verify", "complete");
            displayResult(
                data.repair.final_result
            );
        } else {
            setStep("verify", "failed");
        }

        status.textContent =
            "Repair completed successfully.";

    } catch (error) {

        status.textContent =
            "Repair failed: " + error.message;

        setStep("analysis", "failed");

        console.error(error);

    } finally {

        button.disabled = false;
    }
}


function displayFailure(data) {

    if (!data.tests || data.tests.success) {
        return;
    }

    const card =
        document.getElementById("failureCard");

    const failure =
        document.getElementById("failure");

    failure.textContent =
        data.tests.stdout ||
        data.error ||
        "Test failure detected.";

    card.classList.remove("hidden");
}


function displayAnalysis(analysis) {

    const card =
        document.getElementById("analysisCard");

    const result =
        analysis.analysis;

    if (!result) {
        return;
    }

    document.getElementById("analysis").textContent =
        result.analysis || "";

    document.getElementById("cause").textContent =
        result.suspected_cause || "";

    document.getElementById("confidence").textContent =
        `${Math.round((result.confidence || 0) * 100)}%`;

    card.classList.remove("hidden");
}


function displayRepair(repair) {

    const finalResult =
        repair.final_result || repair;

    const patch =
        finalResult.repair;

    if (!patch) {
        return;
    }

    document.getElementById("repairFile").textContent =
        patch.file || "";

    document.getElementById("repairTarget").textContent =
        patch.target || "";

    document.getElementById("original").textContent =
        patch.original || "";

    document.getElementById("replacement").textContent =
        patch.replacement || "";

    document.getElementById("reason").textContent =
        patch.reason || "";

    document
        .getElementById("repairCard")
        .classList.remove("hidden");
}


function displayResult(result) {

    const card =
        document.getElementById("resultCard");

    const element =
        document.getElementById("result");

    const tests =
        result.verification?.test_result;

    if (result.success) {

        element.className = "success";

        element.textContent =
            `✓ Repair verified — ${
                tests?.stdout?.trim() ||
                "Tests passed"
            }`;

    } else {

        element.className = "error";

        element.textContent =
            "✗ Repair could not be verified.";
    }

    card.classList.remove("hidden");
}