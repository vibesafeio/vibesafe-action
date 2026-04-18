#!/usr/bin/env python3
from __future__ import annotations
"""
tools/cli_scanner.py
VibeSafe instant scan — paste a GitHub URL, get results in 30 seconds.

This is the top-of-funnel: zero friction experience that converts to
GitHub Action installation.

Usage:
  python3 tools/cli_scanner.py https://github.com/user/repo
  python3 tools/cli_scanner.py ./local/path
  python3 tools/cli_scanner.py https://github.com/user/repo --json
"""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent


def clone_repo(url: str, dest: Path) -> bool:
    """Clone a GitHub repo to dest. Returns True on success."""
    try:
        subprocess.run(
            ["git", "clone", "--depth=1", url, str(dest)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=60,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return False


def run_scan(source_path: Path, light: bool = False) -> dict:
    """Run full VibeSafe scan pipeline on a path."""
    results = {
        "path": str(source_path),
        "stack": {},
        "domain": "auto",
        "sast": {},
        "secrets": {},
        "config": {},
        "score": {},
    }

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        # 1. Stack detection
        try:
            r = subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "scanner" / "sast_runner.py"),
                 "--detect-stack", "--path", str(source_path)],
                capture_output=True, text=True, timeout=30,
            )
            if r.returncode == 0:
                results["stack"] = json.loads(r.stdout)
        except Exception:
            pass

        # 2. Domain classification
        try:
            r = subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "scanner" / "domain_rule_engine.py"),
                 "--classify", "--path", str(source_path)],
                capture_output=True, text=True, timeout=30,
            )
            if r.returncode == 0:
                domain_data = json.loads(r.stdout)
                results["domain"] = domain_data.get("best_match", "platform")
        except Exception:
            results["domain"] = "platform"

        # 3. Ruleset selection
        vibe_rules = PROJECT_DIR / "rules" / "vibe-coding.yml"

        if light:
            # Light mode: custom rules only (fast, low memory)
            rules = str(vibe_rules) if vibe_rules.exists() else "p/owasp-top-ten"
            results["scan_mode"] = "light"
        else:
            # Full mode: domain packs + custom rules
            stack = ",".join(results["stack"].get("detected_stack", []))
            langs = ",".join(results["stack"].get("languages", []))
            try:
                r = subprocess.run(
                    [sys.executable, str(SCRIPT_DIR / "scanner" / "domain_rule_engine.py"),
                     "--domain", results["domain"], "--stack", stack, "--languages", langs],
                    capture_output=True, text=True, timeout=30,
                )
                if r.returncode == 0:
                    ruleset = json.loads(r.stdout)
                    rules = ",".join(ruleset.get("semgrep_configs", ["p/owasp-top-ten"]))
                else:
                    rules = "p/owasp-top-ten"
            except Exception:
                rules = "p/owasp-top-ten"

            if vibe_rules.exists():
                rules += f",{vibe_rules}"
            results["scan_mode"] = "full"

        # 4. SAST scan
        sarif_path = tmp_path / "sast.sarif"
        try:
            subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "scanner" / "sast_runner.py"),
                 "--path", str(source_path), "--rules", rules,
                 "--output", str(sarif_path), "--timeout", "120"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, timeout=150,
            )
        except Exception:
            # Create empty SARIF
            sarif_path.write_text(json.dumps({"runs": []}))

        # 5. Secret scan
        secrets_path = tmp_path / "secrets.json"
        try:
            subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "scanner" / "secret_scanner.py"),
                 "--path", str(source_path), "--output", str(secrets_path)],
                capture_output=True, text=True, timeout=60,
            )
        except Exception:
            secrets_path.write_text(json.dumps({"secrets": []}))

        if not secrets_path.exists():
            secrets_path.write_text(json.dumps({"secrets": []}))

        # 6. Config scan
        config_path = tmp_path / "config.json"
        try:
            subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "scanner" / "config_scanner.py"),
                 "--path", str(source_path), "--output", str(config_path)],
                capture_output=True, text=True, timeout=60,
            )
        except Exception:
            config_path.write_text(json.dumps({"findings": []}))

        if not config_path.exists():
            config_path.write_text(json.dumps({"findings": []}))

        # 7. Score calculation
        stack_file = tmp_path / "stack.json"
        stack_file.write_text(json.dumps(results["stack"]))
        try:
            r = subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "report" / "score_calculator.py"),
                 "--domain", results["domain"],
                 "--sast-result", str(sarif_path),
                 "--secret-result", str(secrets_path),
                 "--stack-file", str(stack_file)],
                capture_output=True, text=True, timeout=30,
            )
            if r.returncode == 0:
                results["score"] = json.loads(r.stdout)
        except Exception:
            pass

        # Fallback scoring if score_calculator failed or returned empty
        if not results["score"]:
            total = 0
            high_count = 0
            medium_count = 0
            critical_count = 0
            if sarif_path.exists():
                sarif_data = json.loads(sarif_path.read_text())
                for run in sarif_data.get("runs", []):
                    for r in run.get("results", []):
                        total += 1
                        level = r.get("level", "warning")
                        if level == "error":
                            high_count += 1
                        elif level == "warning":
                            medium_count += 1
            if secrets_path.exists():
                sec = json.loads(secrets_path.read_text())
                for s in sec.get("secrets", []):
                    sev = s.get("severity", "critical")
                    if sev == "critical":
                        critical_count += 1
                    elif sev == "high":
                        high_count += 1
                    elif sev == "medium":
                        medium_count += 1
                    total += 1

            score = max(0, 100 - (critical_count * 20) - (high_count * 10) - (medium_count * 4))
            grade = "A" if score >= 85 else "B" if score >= 70 else "C" if score >= 50 else "D" if score >= 25 else "F"
            results["score"] = {
                "score": score,
                "grade": grade,
                "critical": critical_count,
                "high": high_count,
                "medium": medium_count,
                "low": 0,
                "total_vulnerabilities": total,
            }

        # Load detailed findings for display
        if secrets_path.exists():
            results["secrets"] = json.loads(secrets_path.read_text())
        if sarif_path.exists():
            sarif = json.loads(sarif_path.read_text())
            sast_findings = []
            scan_prefix = str(source_path) + "/"
            for run in sarif.get("runs", []):
                for r in run.get("results", []):
                    level = r.get("level", "warning")
                    severity = {"error": "high", "warning": "medium", "note": "low"}.get(level, "medium")
                    loc = r.get("locations", [{}])[0].get("physicalLocation", {})
                    file_path = loc.get("artifactLocation", {}).get("uri", "")
                    # Strip temp directory prefix
                    if file_path.startswith(scan_prefix):
                        file_path = file_path[len(scan_prefix):]
                    sast_findings.append({
                        "rule_id": r.get("ruleId", ""),
                        "severity": severity,
                        "message": r.get("message", {}).get("text", ""),
                        "file": file_path,
                        "line": loc.get("region", {}).get("startLine", 0),
                    })
            results["sast"]["total"] = len(sast_findings)
            results["sast"]["findings"] = sast_findings[:50]  # Limit to 50 for API
        if config_path.exists():
            results["config"] = json.loads(config_path.read_text())

    return results


def print_results(results: dict):
    """Print scan results in human-readable format."""
    score = results.get("score", {})
    grade = score.get("grade", "?")
    points = score.get("score", "?")
    critical = score.get("critical", 0)
    high = score.get("high", 0)
    medium = score.get("medium", 0)
    low = score.get("low", 0)
    total = score.get("total_vulnerabilities", 0)

    grade_emoji = {"A": "\U0001f7e2", "B": "\U0001f7e1", "C": "\U0001f7e0", "D": "\U0001f534", "F": "\U0001f534"}.get(grade, "?")

    print()
    print("=" * 50)
    print(f"  {grade_emoji} VibeSafe Scan Result: {points}/100 (Grade {grade})")
    print("=" * 50)
    print()

    # Stack info
    stack = results.get("stack", {})
    if stack.get("detected_stack"):
        print(f"  Stack:      {', '.join(stack['detected_stack'])}")
    if stack.get("languages"):
        print(f"  Languages:  {', '.join(stack['languages'])}")
    print(f"  Domain:     {results.get('domain', '?')}")
    print()

    # Severity breakdown
    print(f"  \U0001f534 Critical:  {critical}")
    print(f"  \U0001f7e0 High:      {high}")
    print(f"  \U0001f7e1 Medium:    {medium}")
    print(f"  \U0001f7e2 Low:       {low}")
    print(f"  Total:      {total}")
    print()

    # Certification
    certified = score.get("certified", False)
    if certified:
        print("  \u2705 CERTIFIED — No critical or high vulnerabilities")
    else:
        reason = score.get("certified_block_reason", "")
        if reason:
            print(f"  \u274c Not certified: {reason}")
    print()

    # CTA
    if total > 0:
        print("=" * 50)
        print("  Want this on every PR — automatically?")
        print("  Install in 30 seconds:")
        print()
        print("  github.com/vibesafeio/vibesafe-action")
        print()
        print("  24-line YAML → blocks vulnerable code from merging.")
        print("=" * 50)
    else:
        print("=" * 50)
        print("  \U0001f389 Your code looks clean!")
        print("  Keep it that way — add VibeSafe to every PR:")
        print("  github.com/vibesafeio/vibesafe-action")
        print("=" * 50)

    print()


def main():
    parser = argparse.ArgumentParser(
        description="VibeSafe — instant security scan for any repo",
        usage="python3 tools/cli_scanner.py <github-url-or-path> [--json]",
    )
    parser.add_argument("target", help="GitHub URL (https://github.com/user/repo) or local path")
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of formatted results")
    parser.add_argument("--light", action="store_true", help="Light scan — custom rules only, skip heavy Semgrep packs")
    args = parser.parse_args()

    target = args.target
    cleanup = False
    scan_path = None

    # Determine if URL or local path
    if target.startswith("http://") or target.startswith("https://") or target.startswith("git@"):
        # GitHub URL — clone to temp dir
        if not args.json:
            print(f"\n  Cloning {target}...")
        tmp_dir = Path(tempfile.mkdtemp(prefix="vibesafe-scan-"))
        if not clone_repo(target, tmp_dir):
            if args.json:
                print(json.dumps({"error": f"Could not clone {target}"}))
            else:
                print(f"\n  Error: Could not clone {target}")
                print("  Check the URL and try again.")
            sys.exit(1)
        scan_path = tmp_dir
        cleanup = True
    else:
        scan_path = Path(target)
        if not scan_path.exists():
            print(f"\n  Error: Path not found: {target}")
            sys.exit(1)

    try:
        if not args.json:
            print(f"  Scanning...")
        results = run_scan(scan_path, light=args.light)

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print_results(results)
    finally:
        if cleanup and scan_path:
            shutil.rmtree(scan_path, ignore_errors=True)


if __name__ == "__main__":
    main()
