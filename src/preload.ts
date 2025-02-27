import electron, { contextBridge, ipcRenderer } from "electron";

contextBridge.exposeInMainWorld("electron", {
    ipcRenderer: {
        send: (channel: string, data: any) => ipcRenderer.send(channel, data),
        on: (channel: string, callback: Function) => ipcRenderer.on(channel, (_, data) => callback(data)),
    },
    openExternal: (url: string) => ipcRenderer.invoke('open-external', url),
    getLogs: (amount: number) => ipcRenderer.invoke("get-logs", amount),
    openFile: (path: string) => ipcRenderer.invoke("open-file", path),
    sendEmail: (path: string, name: string, message: string) => ipcRenderer.invoke("send-email", path, name, message),
    textFromPdf: (buffer: ArrayBuffer) => ipcRenderer.invoke("text-from-pdf", buffer),
    getClients: () => ipcRenderer.invoke("get-clients"),
    getTestFile: () => ipcRenderer.invoke("get-test-file"),
    getTemplate: (abbreviation: string) => ipcRenderer.invoke("get-template", abbreviation),
    getLogMessages: () => ipcRenderer.invoke("get-log-messages"),
    createLog: (messages: Array<string>, text: Array<string>, projectData: Record<string,unknown>, fileBuffer: ArrayBuffer) => ipcRenderer.invoke("create-log", messages, text, projectData, fileBuffer),
    getEnvVariable: (variable: string) => ipcRenderer.invoke("get-env-variable", variable),
    updateToken: (token: string) => ipcRenderer.invoke("update-token", token),
});