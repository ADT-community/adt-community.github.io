Closes #4

## What was done

Added `docs/launch/communities.csv` — a research deliverable listing 20 African developer communities to reach for the ADT launch.

Each row includes: community name, country (or Pan-Africa), platform, a direct link, size where publicly known, and concrete guidance on how to post/announce there.

## Acceptance criteria

- [x] 20 communities
- [x] 5+ countries (Nigeria, Kenya, Ghana, South Africa, Ethiopia, Cameroon, Algeria, Tunisia, plus Pan-Africa groups)
- [x] How to post noted for each community

## Validation

A stdlib-only CSV validation (Python `csv.DictReader`) was run against the file:

```
rows: 20
countries: ['Algeria', 'Cameroon', 'Ethiopia', 'Ghana', 'Kenya', 'Nigeria', 'Nigeria / Pan-Africa', 'Pan-Africa', 'South Africa', 'Tunisia']
distinct countries: 10
missing how_to_post: 0
missing link: 0
VALIDATION: PASS
```

No test framework or CI is configured in this repository (static documentation deliverable only); no unrelated files were changed.
