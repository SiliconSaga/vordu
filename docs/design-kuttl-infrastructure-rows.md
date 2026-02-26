# Feature Design: Kuttl Infrastructure Rows

> **Status: TODO** — parked for a future session.

## Problem Statement

Vörðu currently models rows as **feature completion progress** — a scenario
passes once a feature is built and stays passing. This works well for tracking
delivery across projects (Demicracy, Autoboros, etc.).

Platform infrastructure is different: its health is **ephemeral and
cluster-bound**. The GKE test cluster is torn down and rebuilt regularly.
Assertions against it (ArgoCD apps Synced, Gateway Programmed, cert issued)
pass when the cluster is up and healthy, and regress when it is gone.

Two things are needed to support this:
1. A way to ingest kuttl JUnit XML output as Cucumber JSON into Vörðu.
2. A new row "mode" that treats pass/fail as **current state** rather than
   permanent completion — so a failed run doesn't mean "we broke a feature",
   it means "the cluster is not up right now."

## Proposed Integration

### Pipeline

```
kubectl kuttl test --report xml --artifacts-dir /tmp/kuttl-reports/
        ↓
scripts/kuttl2cucumber.py       (convert JUnit XML → Cucumber JSON)
        ↓
POST /ingest → Vörðu            (display in matrix)
```

The converter is ~50–100 lines of Python. It reads kuttl's JUnit XML (one
`<testsuite>` per test case, one `<testcase>` per step) and maps them to the
Cucumber JSON schema that `/ingest` already accepts. Tag metadata
(project/row/phase) is read from a small sidecar YAML file co-located with
each kuttl config.

### Tag Config (sidecar YAML)

```yaml
# nordri/kuttl-vordu-tags.yaml
suite: kuttl-test-gke
project: nordri
tests:
  argocd:
    row: platform
    phase: 0
  gateway:
    row: platform
    phase: 1
  crossplane:
    row: platform
    phase: 1
  velero:
    row: platform
    phase: 2
```

```yaml
# nidavellir/kuttl-vordu-tags.yaml
suite: kuttl-test
project: nidavellir
tests:
  vegvisir:
    row: platform
    phase: 1

suite: kuttl-test-e2e
project: nidavellir
tests:
  whoami:
    row: e2e
    phase: 2
```

### Cucumber JSON shape produced

Each kuttl test case becomes a Scenario; each numbered step file becomes a
Step. Pass/fail maps directly from JUnit `failure` elements.

```json
{
  "keyword": "Feature",
  "name": "Nordri Platform",
  "elements": [
    {
      "keyword": "Scenario",
      "name": "ArgoCD applications healthy",
      "tags": [
        {"name": "vordu:project=nordri"},
        {"name": "vordu:row=platform"},
        {"name": "vordu:phase=0"}
      ],
      "steps": [
        {
          "keyword": "Then",
          "name": "nordri-root Synced+Healthy",
          "result": {"status": "passed", "duration": 1000000}
        }
      ]
    }
  ]
}
```

## New Row Mode: "State" vs "Completion"

The key Vörðu model change needed: rows should support a `mode` field.

| Mode | Semantics | Example |
|------|-----------|---------|
| `completion` | Phase passes once, stays passing (current default) | Feature shipped |
| `state` | Phase reflects the most recent run — can regress | Cluster health |

In `state` mode the matrix cell shows the **latest run result** rather than
the historical best. A cluster that was torn down for the night would show
red/unknown; one that is up and healthy shows green. This is more like a
status dashboard than a progress tracker.

A simple UI indicator (e.g. a small icon or different border style on the
cell) could distinguish state rows from completion rows at a glance.

## Out of Scope (for this design)

- Automating the POST as part of `bootstrap.sh` or CI (post-bootstrap
  hook is the natural place, but requires Vörðu to be reachable from GKE)
- Homelab kuttl tests (Longhorn, Garage assertions) — same pattern, add
  later
- Historical trend view per cluster rebuild cycle (see `design-history-kafka.md`)

## Related

- kuttl tests: `nordri/kuttl-test-gke.yaml`, `nidavellir/kuttl-test.yaml`,
  `nidavellir/kuttl-test-e2e.yaml`
- Vörðu ingest API: `POST /ingest` (Cucumber JSON)
- Existing history design: `docs/design-history-kafka.md`
