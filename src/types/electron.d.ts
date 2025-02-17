declare global {
    interface Window {
        electron: {
            openExternal: (url: string) => Promise<void>;
            getLogs: (amount: number) => Promise<{ dir: string, files: string[] }>;
            openFile: (path: string) => Promise<void>;
            sendEmail: (from: string, to: string, password: string, path: string, name: string, client_secret: any, refresh_token: any, access_token: any) => any;
            textFromPdf: (buffer: ArrayBuffer) => Promise<Array<string>>;
        };
    }
}

export {};