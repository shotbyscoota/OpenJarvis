from openjarvis.security.autonomy import (
    make_autonomous_callback,
    parse_confirmation_prompt,
)
from openjarvis.tools.approval_store import ApprovalStore


def _prompt(tool: str) -> str:
    return f"Allow execution of tool '{tool}' with args {{'x': 1}}?"


def test_parse_prompt():
    assert parse_confirmation_prompt(_prompt("shell_exec"))[0] == "shell_exec"
    assert parse_confirmation_prompt("garbage")[0] == ""


def test_safe_tool_auto_approved():
    assert make_autonomous_callback()(_prompt("shell_exec")) is True


def test_gated_tool_denied_and_queued(tmp_path):
    store = ApprovalStore(str(tmp_path / "a.db"))
    cb = make_autonomous_callback(store)
    assert cb(_prompt("send_sample")) is False
    pending = store.list_pending()
    assert len(pending) == 1
    assert pending[0].action_type == "send_sample"
