import axios, { AxiosResponse } from "axios";
import TokenController from "@/controller/TokenController";

class Request {
    private readonly url: string;
    private token: string;
    private tokenController: TokenController;

    constructor(url: string, token: string) {
        this.url = url;
        this.token = token;
        this.tokenController = new TokenController();
    }

    private prepare(endpoint: string): { url: string; headers: Record<string, string> } {
        const url = `${this.url}${endpoint}`;
        const headers = {
            Accept: "application/json",
            "Content-Type": "application/json",
            Authorization: `Bearer ${this.token}`,
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
                    await this.tokenController.initialize();
                    this.token = await this.tokenController.fetch(); // Fetch new token
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
        return this.handleRequest(() => {
            const { url, headers } = this.prepare(endpoint);
            return axios.get(url, { headers });
        });
    }

    public async post(endpoint: string, data: Record<string, unknown>): Promise<AxiosResponse> {
        return this.handleRequest(() => {
            const { url, headers } = this.prepare(endpoint);
            return axios.post(url, data, { headers });
        });
    }
}

export default Request;
