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

Enable a virtual environment first, PS example: `api\.venv\Scripts\Activate.ps1`
```bash
uvicorn api.main:app --reload
```

API runs on `http://localhost:8000` which also includes the frontend.

* Swagger UI: `http://localhost:8000/docs`
* Ingest Config: `POST /config/ingest`
* Ingest Status: `POST /ingest`

### UI

```bash
cd ui
npm run dev
```

Runs standalone on `http://localhost:5173`.

## Running Tests

To run the full suite (API + UI tests), you must have the services running.

**Option 1: Dev Mode (Two Terminals)**
1.  Start API: `api\.venv\Scripts\Activate.ps1; uvicorn api.main:app --reload`
2.  Start UI: `cd ui; npm run dev`
3.  Run Tests: `pytest`

**Option 2: Integration Mode (Single Port)**
1.  Build UI: `cd ui; npm run build`
2.  Start API: `uvicorn api.main:app` (This serves the built UI at port 8000)
3.  Run Tests: `$env:UI_BASE_URL="http://localhost:8000"; pytest`

## Secure

The API is secured with a simple secret key (`VORDU_API_KEY`) passed as a header `X-API-Key`. Default: `dev-key`.

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
