from __future__ import annotations
"""Shared constants used by multiple VibeSafe tools."""

# Framework conflict map: when key framework is detected, value rule prefixes are false positives
FRAMEWORK_CONFLICTS: dict[str, list[str]] = {
    "flask": ["python.django."],
    "django": ["python.flask."],
    "fastapi": ["python.django.", "python.flask."],
    "express": ["python.django.", "python.flask."],
    "nextjs": ["python.django.", "python.flask."],
    "react": ["python.django.", "python.flask."],
    "vue": ["python.django.", "python.flask."],
    "spring": ["python.flask.", "python.django."],
}

# Noisy rules: always excluded regardless of stack/domain.
# These Semgrep rules have extremely high false positive rates (>95%) and
# produce noise that drowns real findings.  Substring match on rule_id.
NOISY_RULES: list[str] = [
    # Fires on ALL === comparisons in JS/TS, not just password comparisons.
    # vibe-kanban: 25 medium findings all from this single rule.
    # brand-zen: 652 medium findings, majority from this rule.
    "password-comparison-timing",
]
