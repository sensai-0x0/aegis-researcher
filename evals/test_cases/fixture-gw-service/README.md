# Synthetic fixture for case-001-gateway-admin-exposure

A deliberately structured mini-service tree used by `evals/test_cases/`. It is
an AUTHORIZED LOCAL fixture — nothing here is a real target, and the patterns
are documentation-range examples only.

Layout exercised by the case:

```
fixture-gw-service/
├── app.py          # entry point
├── admin.py        # admin route handler (h1 anchor)
└── proxy.cfg       # proxies /admin/* to loopback without auth (h1 rationale)
```

Inventory (worker: system_inventory) must enumerate all three components,
produce one sha256 artifact for the listing, and leave h1 at hypothesis tier
(per evals/expected_results/case-001-expected.yaml).
