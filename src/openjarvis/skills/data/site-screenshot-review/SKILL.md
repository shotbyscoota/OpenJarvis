---
name: site-screenshot-review
description: Render a built site at mobile and desktop sizes, screenshot it, critique the result and fix problems in a loop.
tags: [web, qa, playwright]
---

# Screenshot review loop

1. Serve the output folder locally (`python -m http.server` on a free port, bound to 127.0.0.1).
2. With Playwright, capture full-page screenshots at 390px and 1440px wide.
3. Look at each screenshot and list concrete defects: overflow, cramped or clipped text, low contrast, broken images, weak hierarchy, misaligned grids, console errors.
4. Fix the top defects in the source, re-capture, and compare.
5. Stop after at most 3 rounds or when no major defect remains. Report remaining issues plainly.

Run `page_speed_audit` only on public URLs; it cannot reach localhost. Never deploy from this skill.
