import path from "node:path";

declare global {
    interface Window {
        electron: {
            openExternal: (url: string) => Promise<void>;
            getLogs: (amount: number) => Promise<Array<{ name: string, path: string }>>;
            openFile: (path: string) => Promise<void>;
            sendEmail: (path: string, name: string) => any;
            textFromPdf: (buffer: ArrayBuffer) => Promise<Array<string>>;
            getClients: () => Promise<Array<{ name: string, abbreviation: string, identifier: string, attributeIdentifiers: Record<string, unknown> }>>;
            getTestFile: () => Promise<Buffer>;
            getTemplate: (abbreviation: string) => Promise<Record<string, unknown>>;
            getLogMessages: () => Promise<Record<string, Array<{ type: string; message: string }>>>;
            createLog: (messages: Array<string>, text: Array<string>, projectData: Record<string,unknown>, fileBuffer: ArrayBuffer) => Promise<boolean>;
        };
    }
}

export {};