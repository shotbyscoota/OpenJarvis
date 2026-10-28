---
name: outreach-compliance
description: Checklist applied to every outreach draft before it is queued for approval (CAN-SPAM based; not legal advice).
tags: [outreach, compliance, email]
---

# Outreach compliance check

A draft passes only if all are true. Report each item as pass or fail.

1. From name and address are the real sender.
2. Subject is truthful and matches the body.
3. Message is identifiable as an advertisement (the `send_email` tool appends this).
4. A valid physical postal address is present (appended by `send_email`; `JARVIS_POSTAL_ADDRESS` must be set).
5. A working opt-out is present, and opt-outs are honored within 10 business days. Record them with `add_suppression`; never email a suppressed address.
6. Every claim about the prospect's site is backed by an audit result. No invented numbers, reviews or threats.
7. Recipient address came from a public business listing, not a purchased or harvested list.
8. Sending goes through the approval queue. Do not try to bypass it.

Some states and countries (EU, Canada) require prior consent; if the recipient is outside the US, do not draft and flag it to the user.
