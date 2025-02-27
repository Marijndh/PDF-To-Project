class RequestController {
    protected apiUrl: string;
    protected apiKey: string;
    protected appName: string;
    protected apiToken: string;
    protected isInitialized = false;
    public async initialize(): Promise<void> {
        if (!this.isInitialized) {
            this.apiUrl = await window.electron.getEnvVariable('API_URL') || '';
            this.apiKey = await window.electron.getEnvVariable('API_KEY') || '';
            this.apiToken = await window.electron.getEnvVariable('API_TOKEN') || '';
            this.appName = await window.electron.getEnvVariable('APPLICATION_NAME') || '';
            this.isInitialized = true;
        }
    }
}

export default RequestController;