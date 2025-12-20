def call(Map config = [:]) {
    def catalog = config.catalogPath ?: 'catalog-info.yaml'
    def report = config.reportPath
    // Default to internal K8s service DNS (Service port is 80, target is 8000)
    def apiUrl = config.apiUrl ?: env.VORDU_API_URL ?: 'http://vordu-service.vordu.svc.cluster.local'
    // Prefer environment variable for key if not explicitly passed
    def apiKeyEnv = config.apiKey ? null : 'VORDU_API_KEY'
    def apiKeyVal = config.apiKey

    writeFile file: 'vordu_ingest.py', text: libraryResource('scripts/vordu_ingest.py')

    // Construct command using environment variable for key if possible to avoid leaking in logs
    def cmd = "python3 vordu_ingest.py ${catalog} --api-url ${apiUrl}"
    
    if (report) {
        cmd += " --report ${report}"
    }

    if (apiKeyVal) {
        // If passed explicitly as string, use it (less secure if not masked)
        cmd += " --api-key ${apiKeyVal}"
    } else {
        // Assume VORDU_API_KEY is in the environment (e.g. from withCredentials)
        cmd += " --api-key \$VORDU_API_KEY"
    }

    sh cmd
}
