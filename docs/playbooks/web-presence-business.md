# Web-presence rebuild business: Jarvis workflow

Numbers cited here come from `RESEARCH_NOTES.md`.

## Pipeline
1. `lead-hunter` finds businesses with no site, no HTTPS, or an outdated site
   (Google Places, directories, Maps/Yelp/Facebook listings, Wayback Machine,
   BuiltWith for stack checks). Official APIs only.
2. `web-presence-auditor` verifies each problem and writes a fix list.
3. `outreach-drafter` writes the email from real findings. Drafts only.
4. **Approval gate.** Sending email and `send_sample` go to the approval queue.
5. On a positive reply, `site-builder` makes the sample. Showing it to the
   prospect is the step you approve.
6. `agent-architect` builds extra specialists when a job needs one.

## Outreach rules the drafter follows
Truthful subject, marked as an ad, physical address, opt-out honored within
10 business days. Keep a suppression list and never re-contact opt-outs.

## Outreach draft (two versions, one picked)

Version A
> Subject: Your site takes {load_time} to load on phones
> Hi {first}, I looked at {site}. Three things cost you calls: {issue1}, {issue2}, {issue3}.
> I can show you a rebuilt homepage at no charge. Want me to send one?

Version B
> Subject: Quick note about {business}'s website
> Hi {first}, I help local businesses get found online. I noticed a few things on
> {site} that may be costing you customers, and I'd be glad to send a free sample
> redesign if that's useful.

**Pick: A.** It names specific, checkable findings. {load_time} is filled from the
auditor's measurement; never ship a number it did not measure. Both versions
must carry the ad label, address and opt-out line from the drafter.

## Skills worth adding (note for you)
- Web-performance auditing (Lighthouse/PageSpeed API).
- Local SEO: Google Business Profile, citations, schema markup.
- Conversion copywriting and brand/art direction.
- Image generation and a screenshot-review loop so the builder sees its own pages.
- A CRM export (Apollo and HubSpot connectors are already available to you).
- Hosting/deploy skill (Netlify, Vercel, or Cloudflare Pages), kept behind approval.
- Contract, invoicing and payment-link tooling.

## Honest limits
"Competes with every high-end brand" is a bar the builder approaches through
art direction, real photography and copy, and human review. The model alone
will not reliably reach it. Plan on reviewing each sample before it goes out.
