import axios, { AxiosResponse } from "axios";
import TokenController from "@/controller/TokenController";

class Request {
    private readonly _url: string;
    private _token: string;
    private _tokenController: TokenController;

    constructor(url: string, token: string) {
        this._url = url;
        this._token = token;
        this._tokenController = new TokenController();
    }

    private prepare(endpoint: string): { url: string; headers: Record<string, string> } {
        const url = `${this._url}${endpoint}`;
        const headers = {
            Accept: "application/json",
            "Content-Type": "application/json",
            Authorization: `Bearer ${this._token}`,
        };
        return { url, headers };
    }

    private async handleRequest<T>(requestFn: () => Promise<T>): Promise<T> {
        try {
            return await requestFn();
        } catch (error: any) {
            if (error.response?.status === 403) {
                console.warn("403 received. Refreshing token...");
                try {
                    this._token = await this._tokenController.fetch(); // Fetch new token
                    console.log("Token refreshed, retrying request...");

                    return await requestFn(); // Retry request with new token
                } catch (tokenError) {
                    console.error("Token refresh failed:", tokenError);
                    throw tokenError;
                }
            }
            throw error;
        }
    }

    public async get(endpoint: string): Promise<AxiosResponse> {
        this._token = await this._tokenController.get();
        return this.handleRequest(() => {
            const { url, headers } = this.prepare(endpoint);
            return axios.get(url, { headers });
        });
    }

    public async post(endpoint: string, data: Record<string, unknown>): Promise<AxiosResponse> {
        this._token = await this._tokenController.get();
        return this.handleRequest(() => {
            const { url, headers } = this.prepare(endpoint);
            return axios.post(url, data, { headers });
        });
    }
}

export default Request;
