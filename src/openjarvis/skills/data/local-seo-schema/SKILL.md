---
name: local-seo-schema
description: Add local SEO to a small-business site - title/meta tags, LocalBusiness JSON-LD, heading structure and a citation-consistency checklist.
tags: [seo, web, local-business]
---

# Local SEO and schema

Use on every site the builder produces and when fixing an audited site.

## Per page
- One `<h1>` naming the service and city. Logical `h2`/`h3` below it.
- `<title>`: primary service + city + business name, kept short enough not to truncate.
- `<meta name="description">`: one honest sentence with a reason to click.
- Canonical link, `lang` attribute, descriptive `alt` text, HTTPS.

## LocalBusiness JSON-LD
Put one `application/ld+json` block in `<head>`. Use only facts the owner supplied; omit any field you do not know rather than guessing.

```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "{name}",
  "url": "{url}",
  "telephone": "{phone}",
  "address": {"@type": "PostalAddress", "streetAddress": "{street}",
              "addressLocality": "{city}", "addressRegion": "{state}",
              "postalCode": "{zip}", "addressCountry": "US"},
  "openingHoursSpecification": [],
  "sameAs": []
}
```
Use a more specific `@type` (Plumber, Dentist, Restaurant...) when one fits.

## Citation consistency
Name, address and phone must match exactly across the site, Google Business Profile, Yelp, Facebook and directories. List every mismatch found with its URL. Never invent reviews or ratings; do not add `aggregateRating` unless real reviews exist on the page.

## Verify
Run `page_speed_audit` before and after and report both SEO scores.
