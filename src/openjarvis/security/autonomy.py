"""Autonomy policy — run unattended, but queue outward-facing actions.

Tools that set ``requires_confirmation`` normally block unattended agents
because no confirmation callback exists.  :func:`make_autonomous_callback`
returns a callback that approves everything *except* tools in
``gated_tools``; those are written to the :class:`ApprovalStore` and denied
for now, so the user can approve them later and nothing goes out unseen.
"""

from __future__ import annotations

import logging
import re
from typing import Callable, FrozenSet, Optional

from openjarvis.tools.approval_store import TIER_HIGH, ApprovalStore

logger = logging.getLogger(__name__)

# Actions that leave the machine, publish, or spend money.  Sending sample
# sites to a prospect is the case the user explicitly wants approval for.
DEFAULT_GATED_TOOLS: FrozenSet[str] = frozenset(
    {
        "channel_send",
        "send_email",
        "email_send",
        "send_sample",
        "publish_site",
        "deploy_site",
        "etsy_publish",
        "kdp_publish",
        "purchase",
    }
)

_PROMPT_RE = re.compile(r"tool '([^']+)' with args (.*)\?$", re.DOTALL)


def parse_confirmation_prompt(prompt: str) -> tuple[str, str]:
    """Return ``(tool_name, args_text)`` from a ToolExecutor prompt."""
    match = _PROMPT_RE.search(prompt.strip())
    if match is None:
        return "", prompt
    return match.group(1), match.group(2)


def make_autonomous_callback(
    store: Optional[ApprovalStore] = None,
    *,
    gated_tools: FrozenSet[str] = DEFAULT_GATED_TOOLS,
) -> Callable[[str], bool]:
    """Build a confirm callback: approve all but ``gated_tools``.

    Gated calls are queued in *store* (when given) and denied this run.
    """

    def _callback(prompt: str) -> bool:
        tool, args = parse_confirmation_prompt(prompt)
        if tool not in gated_tools:
            return True
        logger.info("Autonomy policy queued gated tool %s for approval", tool)
        if store is not None:
            store.queue_action(
                action_type=tool,
                description=f"Agent wants to run {tool}",
                payload={"tool": tool, "args": args},
                permission_key=f"{tool}:agent",
                tier=TIER_HIGH,
            )
        return False

    return _callback


__all__ = [
    "DEFAULT_GATED_TOOLS",
    "make_autonomous_callback",
    "parse_confirmation_prompt",
]
