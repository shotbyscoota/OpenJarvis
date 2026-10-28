"""Outreach tools — PageSpeed audit (read-only) and gated, CAN-SPAM-aware email."""

from __future__ import annotations

import os
import smtplib
import sqlite3
from email.message import EmailMessage
from pathlib import Path
from typing import Any

import httpx

from openjarvis.core.paths import get_config_dir
from openjarvis.core.registry import ToolRegistry
from openjarvis.core.types import ToolResult
from openjarvis.security.ssrf import check_ssrf
from openjarvis.tools._stubs import BaseTool, ToolSpec

_PSI_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"


@ToolRegistry.register("page_speed_audit")
class PageSpeedAuditTool(BaseTool):
    """Run a Google PageSpeed Insights audit on a public URL."""

    tool_id = "page_speed_audit"
    is_local = False

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="page_speed_audit",
            description=(
                "Audit a public website with Google PageSpeed Insights. Returns"
                " performance, SEO, accessibility and best-practices scores (0-100)"
                " and key load timings. Set PAGESPEED_API_KEY for higher quota."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Site URL to audit."},
                    "strategy": {
                        "type": "string",
                        "description": "'mobile' (default) or 'desktop'.",
                    },
                },
                "required": ["url"],
            },
            category="network",
            required_capabilities=["network:fetch"],
            timeout_seconds=120.0,
        )

    def execute(self, **params: Any) -> ToolResult:
        url = params.get("url", "")
        if not url:
            return ToolResult(
                tool_name="page_speed_audit", content="No URL provided.", success=False
            )
        ssrf_error = check_ssrf(url)
        if ssrf_error:
            return ToolResult(
                tool_name="page_speed_audit",
                content=f"SSRF protection blocked request: {ssrf_error}",
                success=False,
            )
        query: list[tuple[str, str]] = [
            ("url", url),
            ("strategy", params.get("strategy", "mobile")),
        ]
        query += [
            ("category", c)
            for c in ("performance", "seo", "accessibility", "best-practices")
        ]
        key = os.environ.get("PAGESPEED_API_KEY")
        if key:
            query.append(("key", key))
        try:
            resp = httpx.get(_PSI_URL, params=query, timeout=100)
            resp.raise_for_status()
            data = resp.json()
        except (httpx.HTTPError, ValueError) as exc:
            return ToolResult(
                tool_name="page_speed_audit",
                content=f"PageSpeed request failed: {exc}",
                success=False,
            )
        lh = data.get("lighthouseResult", {})
        scores = {
            k: round((v.get("score") or 0) * 100)
            for k, v in lh.get("categories", {}).items()
        }
        audits = lh.get("audits", {})
        timings = {
            name: audits.get(name, {}).get("displayValue")
            for name in (
                "first-contentful-paint",
                "largest-contentful-paint",
                "total-blocking-time",
                "cumulative-layout-shift",
            )
        }
        lines = [f"Scores (0-100): {scores}", f"Timings: {timings}"]
        return ToolResult(
            tool_name="page_speed_audit",
            content="\n".join(lines),
            success=True,
            metadata={"scores": scores, "timings": timings},
        )


# ---------------------------------------------------------------------------
# Email with suppression list
# ---------------------------------------------------------------------------


def _suppression_db() -> Path:
    return get_config_dir() / "suppression.db"


def add_suppression(address: str, db_path: Path | None = None) -> None:
    """Record an opt-out so no agent emails this address again."""
    path = db_path or _suppression_db()
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS s (addr TEXT PRIMARY KEY)")
        conn.execute("INSERT OR IGNORE INTO s VALUES (?)", (address.strip().lower(),))


def is_suppressed(address: str, db_path: Path | None = None) -> bool:
    path = db_path or _suppression_db()
    if not path.exists():
        return False
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS s (addr TEXT PRIMARY KEY)")
        row = conn.execute(
            "SELECT 1 FROM s WHERE addr = ?", (address.strip().lower(),)
        ).fetchone()
    return row is not None


@ToolRegistry.register("send_email")
class SendEmailTool(BaseTool):
    """Send a commercial email with ad label, postal address and opt-out line.

    Gated: ``requires_confirmation`` plus the autonomy policy's gated list
    mean this never runs without approval.
    """

    tool_id = "send_email"
    is_local = False

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="send_email",
            description=(
                "Send an outreach email over SMTP. Appends the required ad label,"
                " physical address and opt-out line, and refuses suppressed"
                " recipients. Needs JARVIS_SMTP_HOST, JARVIS_SMTP_USER,"
                " JARVIS_SMTP_PASS, JARVIS_FROM and JARVIS_POSTAL_ADDRESS."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "to": {"type": "string"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"},
                },
                "required": ["to", "subject", "body"],
            },
            category="communication",
            requires_confirmation=True,
            required_capabilities=["network:fetch"],
        )

    def execute(self, **params: Any) -> ToolResult:
        def fail(msg: str) -> ToolResult:
            return ToolResult(tool_name="send_email", content=msg, success=False)

        to = params.get("to", "").strip()
        subject = params.get("subject", "").strip()
        body = params.get("body", "")
        if not (to and subject and body):
            return fail("to, subject and body are all required.")
        if is_suppressed(to):
            return fail(f"{to} opted out; not sending.")
        env = os.environ
        missing = [
            k
            for k in (
                "JARVIS_SMTP_HOST",
                "JARVIS_SMTP_USER",
                "JARVIS_SMTP_PASS",
                "JARVIS_FROM",
                "JARVIS_POSTAL_ADDRESS",
            )
            if not env.get(k)
        ]
        if missing:
            return fail(f"Missing configuration: {', '.join(missing)}")

        msg = EmailMessage()
        msg["From"] = env["JARVIS_FROM"]
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(
            f"{body}\n\n--\nThis is an advertisement.\n{env['JARVIS_POSTAL_ADDRESS']}\n"
            "Reply STOP to opt out and I will not contact you again."
        )
        try:
            with smtplib.SMTP(
                env["JARVIS_SMTP_HOST"], int(env.get("JARVIS_SMTP_PORT", "587"))
            ) as smtp:
                smtp.starttls()
                smtp.login(env["JARVIS_SMTP_USER"], env["JARVIS_SMTP_PASS"])
                smtp.send_message(msg)
        except (smtplib.SMTPException, OSError) as exc:
            return fail(f"Send failed: {exc}")
        return ToolResult(
            tool_name="send_email", content=f"Sent to {to}.", success=True
        )
