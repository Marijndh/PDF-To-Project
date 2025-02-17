import fs from "fs";
import nodemailer from "nodemailer";

class LogFile {
    private readonly name: string;
    private readonly path: string;
    private readonly extension: string;
    constructor(fileName: string, path: string) {
        this.path = `${path}/${fileName}`;
        this.name = fileName.substring(0, fileName.lastIndexOf('.'));
        this.extension = fileName.substring(fileName.lastIndexOf('.') + 1);
    }

    public getName(): string {
        return this.name;
    }

    public getPath(): string {
        return this.path;
    }

    public async open(): Promise<void> {
        await window.electron.openFile(this.path);
    }

    public async sendEmail(): Promise<void> {
        const from: string = import.meta.env.VITE_EMAIL_FROM;
        const to: string = import.meta.env.VITE_EMAIL_TO;
        const client_id: string = import.meta.env.VITE_GOOGLE_CLIENT_ID;
        const client_secret: string = import.meta.env.VITE_GOOGLE_CLIENT_SECRET;
        const refresh_token: string = import.meta.env.VITE_GOOGLE_REFRESH_TOKEN;
        const access_token: string = import.meta.env.VITE_GOOGLE_ACCESS_TOKEN;
        console.log(from, to, client_id, client_secret, refresh_token, access_token);
        await window.electron.sendEmail(from, to, this.path, this.name, client_id, client_secret, refresh_token, access_token);
    }
}
export default LogFile;