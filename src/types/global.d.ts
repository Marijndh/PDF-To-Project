export {};

declare global {
    interface Window {
        electron: {
            ipcRenderer: {
                send: (channel: string, data?: any) => void;
                on: (channel: string, callback: (data: any) => void) => void;
            };
        };
    }
}