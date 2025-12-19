def call(Map config = [:]) {
    // config.catalogPath (required)
    // config.reportPath (optional)
    // config.apiUrl (optional, defaults to VORDU_API_URL env var)
    // config.apiKey (optional, defaults to VORDU_API_KEY env var)

    def catalog = config.catalogPath ?: 'catalog-info.yaml'
    def report = config.reportPath
    def apiUrl = config.apiUrl ?: env.VORDU_API_URL ?: 'http://vordu-api:8000'
    def apiKey = config.apiKey ?: env.VORDU_API_KEY

    // Ensure we have the ingestion script. 
    // In a real library, we might use 'libraryResource' to write it to disk.
    // For now, we assume it's checked out or present.
    // Let's assume the library writes it to a tmp location.
    
    writeFile file: 'vordu_ingest.py', text: libraryResource('scripts/vordu_ingest.py')

    def cmd = "python3 vordu_ingest.py ${catalog} --api-url ${apiUrl}"
    if (report) {
        cmd += " --report ${report}"
    }
    if (apiKey) {
        cmd += " --api-key ${apiKey}"
    }

    sh cmd
}
