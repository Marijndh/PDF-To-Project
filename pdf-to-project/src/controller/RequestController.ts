class RequestController {
    protected readonly apiUrl: string;
    protected readonly apiKey: string;
    protected apiToken: string;
    protected readonly appName: string;

    constructor() {
        this.apiUrl = import.meta.env.VITE_API_URL;
        this.apiKey = import.meta.env.VITE_API_KEY;
        this.apiToken = import.meta.env.VITE_API_TOKEN;
        this.appName = import.meta.env.VITE_APPLICATION_NAME;
    }
}

export default RequestController;