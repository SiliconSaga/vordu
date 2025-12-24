# Vörðu

*The Landmark - Roadmap Visualization*

> "A cairn or pile of stones used as a waymarker."

**Vörðu** is a **Visualization Tool** for Demicracy and other projects. It reads Backstage-flavored catalog details then finds and parses BDD test results and renders it as a dynamic, interactive roadmap, helping us see where we are on the path.

## Tech Stack

* Node.js & Python
* Backend DB to store data sets
* Relies on Jenkins for builds and separate ingestion in other projects using a Jenkins lib from this project

## Run

How to run locally (on Windows for the moment)

### API

**Prerequisites:**
*   Python 3.11
*   `pip install -r api/requirements.txt`
*   `playwright install` (Required for UI tests)

Enable a virtual environment first:
*   **Windows (PowerShell):** `api\.venv\Scripts\Activate.ps1`
*   **Mac/Linux:** `source api/.venv/bin/activate`

```bash
uvicorn api.main:app --reload
```

API runs on `http://localhost:8000` which also includes the frontend.

* Swagger UI: `http://localhost:8000/docs`
* Ingest Config: `POST /config/ingest`
* Ingest Status: `POST /ingest`

### UI

**Prerequisites:**
*   Node.js 20.19+ or 22.12+ (Use `fnm`, `nvm`, or `nodenv` to manage versions)
*   `npm install`

```bash
cd ui
npm run dev
```

Runs standalone on `http://localhost:5173`.

## Running Tests

To run the full suite (API + UI tests), you must have the services running.

### Option 1: Dev Mode (Two Terminals)

* Start API (Windows): `api\.venv\Scripts\Activate.ps1; uvicorn api.main:app --reload`
* Start API (Mac): `source api/.venv/bin/activate; uvicorn api.main:app --reload`
* Start UI: `cd ui; npm run dev`
* Run Tests: `pytest`

### Option 2: Integration Mode (Single Port)

* Build UI: `cd ui; npm run build`
* Start API: `uvicorn api.main:app` (This serves the built UI at port 8000)
* Run Tests:
  * Windows: `$env:UI_BASE_URL="http://localhost:8000"; pytest`
  * Mac/Linux: `export UI_BASE_URL="http://localhost:8000"; pytest`

## Secure

The API is secured with a simple secret key (`VORDU_API_KEY`) passed as a header `X-API-Key`. Default is `dev-key` while a secret one is stored in Jenkins and used in the pipeline as a credential.

## Jenkins Integration

Vörðu provides a **Jenkins Shared Library** for standardized BDD ingestion.

### 1. Installation

**Method A: JCasC (Automated)**

Add the contents of `ci/jcasc-library-config.yaml` to your Jenkins Configuration as Code:

```yaml
unclassified:
  globalLibraries:
    libraries:
      - name: "vordu-lib"
        defaultVersion: "main"
        retriever:
          modernSCM:
            scm:
              git:
                remote: "https://github.com/SiliconSaga/vordu.git"
```

**Method B: Manual**

Go to `Manage Jenkins` -> `System` -> `Global Pipeline Libraries`.

*   Name: `vordu-lib`
*   Default Version: `main`
*   Retrieval Method: Modern SCM -> Git -> Repo URL: `https://github.com/SiliconSaga/vordu.git`

### 2. Usage

In your project's `Jenkinsfile`:

```groovy
@Library('vordu-lib') _

pipeline {
    agent any
    stages {
        stage('Ingest Test Results') {
            steps {
                ingestVordu(
                    catalogPath: 'catalog-info.yaml',
                    reportPath: 'cucumber.json', // Optional, defaults to mock
                    apiUrl: 'http://vordu-api:8000' // Optional override
                )
            }
        }
    }
}
```

### 3. Manual Ingestion (Local)

You can also run the ingestion process locally without Jenkins, which is useful for development.

**Prerequisites:**
1.  **Generate `cucumber.json`**: Ensure you have `pytest-cucumberjs` installed (`pip install pytest-cucumberjs`).
    ```bash
    pytest --cucumberjson=cucumber.json
    ```
2.  **Vörðu API**: Ensure the API is running locally (default: `http://localhost:8000`).

**Run the Ingest Script:**

```bash
# syntax: python resources/scripts/vordu_ingest.py <catalog-path> --report <report-path> --api-url <url>
python resources/scripts/vordu_ingest.py catalog-info.yaml --report cucumber.json --api-url http://localhost:8000
```

## Feature File Tagging & Conventions

Vörðu relies on associating BDD scenarios with specific Roadmap components. To minimize maintenance overhead, the ingestion pipeline uses a "Convention over Configuration" approach to deduce which component a feature file belongs to.

### Priority Resolution Logic

The system resolves the target component for a feature file using the following priority order (highest to lowest):

| Priority | Convention Source | Pattern | Example | Logic |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Explicit Tag** | `@vordu:row=X` | `@vordu:row=vordu-api` | **Always wins.** Use this to override conventions. |
| **2** | **Subdirectory** | `features/<name>/*.feature` | `features/api/users.feature` | `<name>` is appended to the System Name (e.g. `vordu-api`). |
| **3** | **Filename** | `features/<name>.feature` | `features/api.feature` | `<name>` is appended to the System Name (e.g. `vordu-api`). |
| **4** | **System Default** | Root `*.feature` | `features/history.feature` | Defaults to System Row (if supported) or requires System Tag. |

### Other Tags

*   **`@wip`**: Marks a scenario as "Work In Progress".
    *   **Behavior**:
        *   Status is forced to **Pending**.
        *   Step counts are hidden (treated as **Planned/0 steps**).
        *   Useful for planning future work without polluting the "Failed" metrics.
*   **`@vordu:phase=N`**: Explicitly assigns a scenario to a Roadmap Phase (0-3).
