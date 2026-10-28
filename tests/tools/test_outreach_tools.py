from unittest.mock import MagicMock, patch

import openjarvis.tools.outreach_tools as ot
from openjarvis.tools.outreach_tools import (
    PageSpeedAuditTool,
    SendEmailTool,
    add_suppression,
    is_suppressed,
)

ENV = {
    "JARVIS_SMTP_HOST": "smtp.example.com",
    "JARVIS_SMTP_USER": "u",
    "JARVIS_SMTP_PASS": "p",
    "JARVIS_FROM": "me@example.com",
    "JARVIS_POSTAL_ADDRESS": "1 Main St, Town, ST 00000",
}


def test_email_requires_confirmation():
    assert SendEmailTool().spec.requires_confirmation is True


def test_email_missing_config(monkeypatch):
    for k in ENV:
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setattr(ot, "is_suppressed", lambda a: False)
    r = SendEmailTool().execute(to="a@b.com", subject="s", body="b")
    assert not r.success and "JARVIS_POSTAL_ADDRESS" in r.content


def test_email_suppressed(tmp_path, monkeypatch):
    db = tmp_path / "s.db"
    add_suppression("A@B.com", db)
    assert is_suppressed("a@b.com", db)
    monkeypatch.setattr(ot, "is_suppressed", lambda a: is_suppressed(a, db))
    r = SendEmailTool().execute(to="a@b.com", subject="s", body="b")
    assert not r.success and "opted out" in r.content


def test_email_footer_appended(monkeypatch):
    for k, v in ENV.items():
        monkeypatch.setenv(k, v)
    monkeypatch.setattr(ot, "is_suppressed", lambda a: False)
    with patch("smtplib.SMTP") as smtp:
        r = SendEmailTool().execute(to="a@b.com", subject="s", body="hello")
    assert r.success
    sent = smtp.return_value.__enter__.return_value.send_message.call_args[0][0]
    text = sent.get_content()
    assert "advertisement" in text and ENV["JARVIS_POSTAL_ADDRESS"] in text
    assert "opt out" in text


def test_pagespeed_parses_scores():
    fake = MagicMock()
    fake.json.return_value = {
        "lighthouseResult": {
            "categories": {"performance": {"score": 0.42}, "seo": {"score": 1}},
            "audits": {"first-contentful-paint": {"displayValue": "2.1 s"}},
        }
    }
    with patch("httpx.get", return_value=fake), patch.object(
        ot, "check_ssrf", return_value=None
    ):
        r = PageSpeedAuditTool().execute(url="https://example.com")
    assert r.success and r.metadata["scores"] == {"performance": 42, "seo": 100}


def test_pagespeed_blocks_private_url():
    r = PageSpeedAuditTool().execute(url="http://127.0.0.1/")
    assert not r.success
