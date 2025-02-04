import { contextBridge, ipcRenderer } from "electron";

contextBridge.exposeInMainWorld("electron", {
    ipcRenderer: {
        send: (channel: string, data: any) => ipcRenderer.send(channel, data),
        on: (channel: string, callback: Function) => ipcRenderer.on(channel, (_, data) => callback(data)),
    },
    openExternal: (url: string) => ipcRenderer.invoke('open-external', url),
});