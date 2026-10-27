# Etsy / KDP coloring-book automation

Numbers cited here come from `RESEARCH_NOTES.md`.

## Pipeline
1. `etsy-product-researcher` ranks niches (demand, competition, price bands).
2. Generate line art; check each page: clean black lines, no gray shading,
   no near-duplicates.
3. Assemble the PDF. KDP needs at least 24 pages at 8.5" x 11".
4. Build listing assets: preview images (Etsy wants previews), title, tags, description.
5. Disclose AI use: the Etsy listing note plus "Designed by seller", and the KDP
   checkbox at title setup.
6. **Approval gate.** `etsy_publish` and `kdp_publish` are gated; nothing goes live unseen.
7. Learn from sales data: feed views, favorites and sales back to the researcher.

## Risks
- The market is crowded and I found no saturation data. Differentiate by
  theme, audience and quality, not volume.
- The cap of 3 titles per day is unverified; do not mass-publish.
- Check Etsy's and KDP's own policy pages before the first listing.
