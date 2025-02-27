import RequestController from "@/controller/RequestController";
import Request from "@/entity/Request";

export default class TokenController extends RequestController {
    public async fetch(): Promise<string> {
        const request = new Request(this.apiUrl, this.apiToken);
        const endpoint = `/auth/login/${this.appName}/apiKey?apiKey=${this.apiKey}`;
        const response = await request.post(endpoint, {});
        await window.electron.updateToken(response.data['token'])
        return response.data['token'];
    }
}