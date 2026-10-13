/**
 * Rule demonstration corresponding to agents/workers.py and agents/supervisor.py.
 * No API calls, patient data storage, predictive modeling, or cryptographic audit.
 */
export function evaluateTask(input) {
    const taskId = String(input.task_id ?? "").trim();
    const target = String(input.target_identifier ?? "").trim();
    const status = String(input.status_descriptor ?? "NOMINAL").trim();
    const primaryText = String(input.primary_metric ?? "").trim();
    const secondaryText = String(input.secondary_metric ?? "").trim();
    const primary = primaryText === "" ? NaN : Number(primaryText);
    const secondary = secondaryText === "" ? NaN : Number(secondaryText);
    const critical = input.is_critical_flag === true;

    if (!taskId || !target) throw new Error("Task and target identifiers are required.");
    if (!Number.isFinite(primary) || !Number.isFinite(secondary)) {
        throw new Error("Both metrics must be finite numeric values.");
    }
    if (taskId.length > 150 || target.length > 150 || status.length > 200) {
        throw new Error("Input text exceeds the maximum permitted length.");
    }

    const alerts = [];
    function add(worker, urgency, summary, technicalDetails, remediation) {
        alerts.push({
            origin_worker: worker,
            urgency,
            summary,
            technical_details: technicalDetails,
            actionable_remediation: remediation
        });
    }
    if (primary > 25) {
        add("InvariantQCWorker", "ELEVATED_RISK",
            "Primary Metric Threshold Exceeded",
            `Primary measurement (${primary.toFixed(2)}) is above the demonstration threshold (25.00).`,
            "Review the configured primary threshold and investigate the observation.");
    }
    if (critical || secondary > 12) {
        add("SafetyEscalationWorker", critical ? "CRITICAL_STAT_PANIC" : "ELEVATED_RISK",
            "Priority or Secondary Threshold Triggered",
            `Critical flag: ${critical}; secondary index: ${secondary.toFixed(2)} (threshold: 12.00).`,
            "Review local escalation protocols before taking any operational action.");
    }
    if (["DISCORDANT", "ANOMALY", "MUTANT", "VIOLATION", "FAIL", "REJECT"].some(word =>
        status.toUpperCase().includes(word))) {
        add("ProtocolConformanceWorker", "ELEVATED_RISK",
            "Protocol Descriptor Flagged",
            "The supplied descriptor matches an illustrative anomaly keyword.",
            "Verify the original specimen record and local procedures.");
    }

    const criticalCount = alerts.filter(a => a.urgency === "CRITICAL_STAT_PANIC").length;
    const elevatedCount = alerts.filter(a => a.urgency === "ELEVATED_RISK").length;
    const overall = criticalCount ? "CRITICAL_STAT_PANIC" :
        elevatedCount ? "ELEVATED_RISK" : "ROUTINE";

    return {
        mode: "browser-local rule demonstration",
        task_id: taskId,
        target_identifier: target,
        primary_metric: primary,
        secondary_metric: secondary,
        status_descriptor: status || "NOMINAL",
        is_critical_flag: critical,
        overall_urgency: overall,
        integrity_status: criticalCount ? "RECALIBRATION_REQUIRED" :
            elevatedCount ? "DISCORDANT_ANOMALY" : "VALIDATED_OPTIMAL",
        total_alerts: alerts.length,
        critical_alerts_count: criticalCount,
        alerts,
        cryptographic_audit: "Not available in browser-only mode",
        disclaimer: "Illustrative thresholds, not validated laboratory TAT predictions or clinical decision support"
    };
}

if (typeof document !== "undefined") {
    const form = document.getElementById("audit-form");
    const output = document.getElementById("output");
    const error = document.getElementById("error");
    const download = document.getElementById("download");
    const reset = document.getElementById("reset");
    const counters = {processed: 0, critical: 0, elevated: 0, routine: 0};
    let latest = null;

    function updateCounters() {
        for (const [key, value] of Object.entries(counters)) {
            document.getElementById("count-" + key).textContent = String(value);
        }
    }

    form.addEventListener("submit", event => {
        event.preventDefault();
        error.textContent = "";
        try {
            const fields = new FormData(form);
            latest = evaluateTask({
                task_id: fields.get("task_id"),
                target_identifier: fields.get("target_identifier"),
                primary_metric: fields.get("primary_metric"),
                secondary_metric: fields.get("secondary_metric"),
                status_descriptor: fields.get("status_descriptor"),
                is_critical_flag: fields.get("is_critical_flag") === "on"
            });
            output.textContent = JSON.stringify(latest, null, 2);
            counters.processed += 1;
            if (latest.overall_urgency === "CRITICAL_STAT_PANIC") counters.critical += 1;
            else if (latest.overall_urgency === "ELEVATED_RISK") counters.elevated += 1;
            else counters.routine += 1;
            updateCounters();
            download.disabled = false;
        } catch (exc) {
            error.textContent = exc.message || "Input could not be evaluated.";
        }
    });

    download.addEventListener("click", () => {
        if (!latest) return;
        const blob = new Blob([JSON.stringify(latest, null, 2) + "\n"],
            {type: "application/json"});
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "lab-tat-rule-result.json";
        a.click();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
    });

    reset.addEventListener("click", () => {
        form.reset();
        latest = null;
        error.textContent = "";
        output.textContent = "No evaluation yet. Enter synthetic data and select Evaluate.";
        Object.keys(counters).forEach(key => { counters[key] = 0; });
        updateCounters();
        download.disabled = true;
    });
}
