from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REHEARSAL_RUNBOOK = REPO_ROOT / "docs" / "operator-prelaunch-rehearsal-runbook.md"
EVIDENCE_TEMPLATE = REPO_ROOT / "docs" / "operator-prelaunch-evidence-template.md"
RELEASE_RUNBOOK = REPO_ROOT / "docs" / "operator-release-baseline.md"
ACCEPTANCE_CHECKLIST = REPO_ROOT / "docs" / "operator-launch-acceptance-checklist.md"


def test_prelaunch_rehearsal_packet_is_linked_from_launch_baseline() -> None:
    rehearsal_runbook = REHEARSAL_RUNBOOK.read_text(encoding="utf-8")
    release_runbook = RELEASE_RUNBOOK.read_text(encoding="utf-8")
    acceptance_checklist = ACCEPTANCE_CHECKLIST.read_text(encoding="utf-8")

    assert REHEARSAL_RUNBOOK.exists()
    assert EVIDENCE_TEMPLATE.exists()
    assert "pnpm test:launch-readiness:signoff" in rehearsal_runbook
    assert "operator-prelaunch-rehearsal-runbook.md" in release_runbook
    assert "operator-prelaunch-evidence-template.md" in release_runbook
    assert "operator-prelaunch-rehearsal-runbook.md" in acceptance_checklist
    assert "operator-prelaunch-evidence-template.md" in acceptance_checklist


def test_prelaunch_rehearsal_packet_captures_go_no_go_and_epic14_escalation() -> None:
    rehearsal_runbook = REHEARSAL_RUNBOOK.read_text(encoding="utf-8")
    evidence_template = EVIDENCE_TEMPLATE.read_text(encoding="utf-8")

    assert "Go / No-Go Rules" in rehearsal_runbook
    assert "Epic 14" in rehearsal_runbook
    assert "Oracle" in rehearsal_runbook
    assert "pnpm test:oracle-runtime:signoff" in rehearsal_runbook
    assert "Go / No-Go" in evidence_template
    assert "评估 Epic 14" in evidence_template
    assert "pnpm test:launch-readiness:signoff" in evidence_template
