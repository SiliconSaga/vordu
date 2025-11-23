# Vörðu

*The Landmark - Roadmap Visualization*

> "A cairn or pile of stones used as a waymarker."

**Vörðu** is a **Visualization Tool** for Demicracy and other project. It reads the matrixed roadmap and renders it as a dynamic, interactive guide, helping us see where we are on the path.

## Tech Stack

* **Runtime**: Node.js
* **Purpose**: Dynamic Roadmap Rendering

### Validate

* Main site should be available at https://vordu.siliconsaga.org
* Look for API health check at https://vordu.siliconsaga.org/health

### Secure

The API is secured with a simple secret key that should be stored as a Jenkins credential then passed to the deployment as `VORDU_API_KEY`

* Jenkins Credential: Create a "Secret Text" credential in Jenkins named `vordu-api-key` with a strong random string.
* `kubectl create secret generic vordu-secrets --from-literal=api-key=YOUR_SECRET_STRING -n vordu`