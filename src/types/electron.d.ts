export declare global {
    interface Window {
        electron: {
            openExternal: (url: string) => Promise<void>;
            openFile: (path: string) => Promise<void>;
            sendEmail: (path: string, name: string, message: string) => Promise<void>;
            textFromPdf: (buffer: ArrayBuffer) => Promise<Array<string>>;
            getClients: () => Promise<Array<{ name: string, abbreviation: string, identifier: string, attributeIdentifiers: Record<string, unknown> }>>;
            createLog: (messages: Array<string>, text: Array<string>, projectData: Record<string,unknown>, fileBuffer: ArrayBuffer, projectObject: string) => Promise<boolean>;
            getEnvVariable: (variable: string) => Promise<string | undefined>;
            updateToken: (token: string) => Promise<void>;
            getLogs: (amount: number) => Promise<Array<{ name: string, path: string }>>;
            getTestFile: () => Promise<Buffer>;
            getTemplate: (abbreviation: string) => Promise<Record<string, unknown>>;
            getLogMessages: () => Promise<Record<string, Array<{ type: string; message: string }>>>;
        };
    }
}