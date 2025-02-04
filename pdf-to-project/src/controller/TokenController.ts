import RequestController from "@/controller/RequestController";
import Request from "@/entity/Request";

class TokenController extends RequestController {
    private set(token: string): void {
        window.electron.ipcRenderer.send("update-token", token);
    }

    public async fetch(): Promise<string> {
        const request = new Request(this.apiUrl, this.apiToken);
        const endpoint = `/auth/login/${this.appName}/apiKey?apiKey=${this.apiKey}`;
        const response = await request.post(endpoint, {});
        this.set(response.data['token'])
        return response.data['token'];
    }
    public async get(): Promise<string> {
        if (this.apiToken === '') this.apiToken = await this.fetch();
        return this.apiToken;
    }
}

export default TokenController;