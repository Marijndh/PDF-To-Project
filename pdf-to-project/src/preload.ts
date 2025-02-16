import electron, { contextBridge, ipcRenderer } from "electron";

contextBridge.exposeInMainWorld("electron", {
    ipcRenderer: {
        send: (channel: string, data: any) => ipcRenderer.send(channel, data),
        on: (channel: string, callback: Function) => ipcRenderer.on(channel, (_, data) => callback(data)),
    },
    openExternal: (url: string) => ipcRenderer.invoke('open-external', url),
    getLogs: (amount: number) => ipcRenderer.invoke("get-logs", amount),
    openFile: (path: string) => ipcRenderer.invoke("open-file", path),
    sendEmail: (from: string, to: string, path: string, name: string, client_id: string, client_secret: string, refresh_token: string, access_token: string) => ipcRenderer.invoke("send-email", from, to, path, name, client_id, client_secret, refresh_token, access_token),
    textFromPdf: (buffer: ArrayBuffer) => ipcRenderer.invoke("text-from-pdf", buffer),
});