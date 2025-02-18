import ProjectBuilder from "@/utils/ProjectBuilder";
import Client from "@/entity/Client";
import {Log} from "@/entity/Log";

export default class ProjectExtractor {
    private client: Client;
    private text: Array<string>;
    private template: Record<string, unknown>;
    private attributeIdentifiers: Record<string, unknown>
    private projectData: Record<string, unknown>;
    private projectBuilder: ProjectBuilder;

    constructor() {}

    public setText(text: Array<string>): void {
        this.text = text;
    }

    public getText(): Array<string> {
        return this.text;
    }

    public async findClient(): Promise<boolean> {
        const clients = (await window.electron.getClients()).map(
          (client: any) => new Client(client.name, client.abbreviation, client.identifier, client.attributeIdentifiers)
        );
        for (const client of clients) {
            const identifierIndex = this.text.findIndex(text => text.toLowerCase() === client.getIdentifier().toLowerCase());
            if (identifierIndex !== -1) {
                this.client = client;
                this.text = this.text.slice(identifierIndex);
                return true;
            }
        }
        return false;
    }

    public async fetchTemplate(): Promise<boolean> {
        const template = await window.electron.getTemplate(this.client.getAbbreviation());
        if (template) {
            this.template = template;
            return true;
        }
        return false;
    }

    private extractValue(identifier: string, range: string, type: string): string | null {
        if (type === "R" && identifier) {
            const regex = new RegExp(identifier);
            const index = this.text.findIndex(word => regex.test(word));
            if (index !== -1) {
                const [start, end] = range.split("|").map(Number);
                return this.text[index + start] || null;
            }
        } else if (type === "S" && identifier) {
            const index = this.text.indexOf(identifier);
            if (index !== -1) {
                const [start, end] = range.split("|").map(Number);
                return this.text[index + start] || null;
            }
        }
        return null;
    }

    public setProjectValues(): void {

    }

    public insertProjectIntoTemplate(): void {
        this.projectData = {};
    }

    public async logData(logs: Array<Log>, file: File): Promise<boolean> {
        const messages = logs.map(log => log.getMessage());
        const arrayBuffer = await file.arrayBuffer();
        return window.electron.createLog(messages, this.text, this.projectData, arrayBuffer);
    }

    public getClient(): string {
        return this.client.getName();
    }

    public getProjectData(): Record<string, unknown> {
        return this.projectData;
    }
}