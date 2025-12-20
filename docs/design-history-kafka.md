# Feature Design: Vörðu History & Analytics

Note that this is also referred to by the `history.feature` BDD file.

## Problem Statement
Currently, Vörðu maintains only the **Current State** (Snapshot) of the roadmap matrix.
*   **Data Loss**: Older test runs are overwritten.
*   **Granularity Conflicts**: Changing granularity (e.g., Component -> System) leaves "Ghost Rows" or requires destructive syncs.
*   **No Trends**: We cannot visualize progress over time (e.g., "Are we burning down the technical debt?").

## Architecture Proposal: Event Log (Insert-Only)

We propose moving to an **Append-Only** architecture, consistent with Event Sourcing principles.

### 1. Data Store (Kafka / Logical Event Log)
Instead of updating rows, every Ingestion Event is a new record.

**Event Schema**:
```json
{
  "event_id": "uuid",
  "timestamp": "2025-12-20T12:00:00Z",
  "run_id": "jenkins-build-102",
  "system": "mimir",
  "granularity": "system",
  "rows": [
    { "row_id": "mimir", "phase": 0, "status": "pass", "completion": 100 }
  ]
}
```

### 2. Database Schema Changes (SQL Implementation)
If Kafka is not available immediately, we can implement this pattern in Postgres/SQLite:

*   **Table**: `MatrixHistory` (or modifying `MatrixCell`)
*   **New Column**: `run_id` (String/UUID), `created_at` (Timestamp).
*   **Constraint Changes**: Remove unique constraints on `(project, row, phase)`.

### 3. Query Logic ("The Blender")
The UI (or API) is responsible for resolving the current view.

*   **Latest View**:
    ```sql
    SELECT * FROM MatrixHistory 
    WHERE run_id = (
        SELECT run_id FROM MatrixRuns 
        WHERE system = 'mimir' 
        ORDER BY created_at DESC LIMIT 1
    )
    ```
    *   *Result*: This naturally filters out old "Component" rows when granularity switches to "System", because the latest run only contains the System row.
    
*   **Trend View**:
    ```sql
    SELECT created_at, SUM(scenarios_total) as total, SUM(scenarios_passed) as passed
    FROM MatrixHistory
    WHERE system = 'mimir'
    GROUP BY run_id
    ```
    *   *Result*: We can plot 6 points (Component era) and then 1 point (System era) on the same graph without data loss.

## Implementation Steps
1.  **Phase 1 (MVP)**: Add `run_id` to schema. switch Ingest to Insert-Only. Update `/matrix` endpoint to query `MAX(run_id)`.
2.  **Phase 2 (Trends)**: Add `/matrix/history` endpoint for graphing.
3.  **Phase 3 (Kafka)**: Move ingestion to a Kafka Topic. API consumes topic to populate the Read Database.
