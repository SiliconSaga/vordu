# Vörðu Architecture Options
*Choosing the Data Flow for the Living Roadmap*

## Context
*   **Goal**: Visualize roadmap maturity across the Yggdrasil ecosystem.
*   **Source of Truth**:
    *   **Phases (Columns)**: Defined globally in `yggdrasil/roadmap-schema.yaml` (Exists!).
    *   **Capabilities (Rows)**: Defined per-project (e.g., `demicracy/roadmap.yaml`).
    *   **Status**: Defined by BDD Test Results (Cucumber JSON) generated in Jenkins.

## Option 1: The "Push" Model (Recommended)
*The "Uplifted Mascot" Approach.*

### How it works
1.  **Discovery**: Projects register themselves in `yggdrasil/roadmap-schema.yaml` (or a `bom.json`).
2.  **Ingestion**: During the Jenkins build, the pipeline runs a script (`notify_vordu.py`) that:
    *   Parses the local `roadmap.yaml` (for row definitions).
    *   Parses the `cucumber.json` (for test status).
    *   POSTs a unified ID/Status payload to the Vörðu API.
3.  **State**: Vörðu stores the latest state in its own DB (SQLite/Postgres).

### Pros
*   **Real-time**: The dashboard updates seconds after a build finishes.
*   **Decoupled**: Vörðu doesn't need to know *how* to build or scan every repo; it just waits for data.
*   **History**: The DB can easily track "Pass Rate over Time" for velocity charts.

### Cons
*   **Infrastructure**: Requires running the Vörðu API and a DB.

---

## Option 2: The "Pull" Model (Static Site)
*The "Backstage" Approach.*

### How it works
1.  **Discovery**: Vörðu scans `yggdrasil/roadmap-schema.yaml` to find project paths.
2.  **Ingestion**: A scheduled job (cron) in Vörðu executes `git pull` on all repos.
3.  **Parsing**: It directly reads the `roadmap.yaml` and `test-results.json` files from the disk.

### Pros
*   **Simple**: No API, no DB. Just a script reading files and generating a static HTML page.
*   **GitOps**: The state is exactly what is on the disk.

### Cons
*   **Slow**: Updates happen on schedule, not event-driven.
*   **Heavy**: Vörðu needs access to clone/pull all repos (Permission issues?).
*   **Stale**: If CI fails to commit the `test-results.json` back to the repo (an anti-pattern), the dashboard is wrong.

---

## Option 3: The "Hybrid" Model
*Discovery via File, Status via Event.*

1.  **Discovery**: Vörðu reads `yggdrasil/roadmap-schema.yaml` to build the "Empty Skeleton" of the table.
2.  **Status**: Jenkins pushes *only* the Test Results to a lightweight "Status Collector" (like a Redis stream).
3.  **Rendering**: The UI combines the static Skeleton (from Git) with the dynamic Status (from Redis).

---

## Recommendation
**Go with Option 1 (Push)**.
*   It aligns with the **Uplifted Mascot** pattern (Agents submitting knowledge).
*   It avoids the "Committed Test Results" anti-pattern of Option 2.
*   It allows Vörðu to run locally *or* centrally without massive Git permissions.

### Proposed Vörðu Schema (DB)
```json
{
  "project_id": "demicracy",
  "rows": [
    { "id": "identity", "label": "Identity" }
  ],
  "features": [
    { "row_id": "identity", "phase": 1, "status": "passed", "feature_name": "Login" }
  ],
  "last_updated": "2024-05-20T10:00:00Z"
}
```
