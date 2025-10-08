import ProjectBuilder from "@/utils/ProjectBuilder";
import Client from "@/entity/Client";
import {LogLine} from "@/entity/LogLine";
import {AttributeIdentifier} from "@/entity/AttributeIdentifier";
import Project from "@/entity/Project";
import {AttributeType} from "@/enums/AttributeType";

export default class ProjectExtractor {
    private client: Client;
    private text: Array<string>;
    private template: Record<string, unknown>;
    private projectBuilder: ProjectBuilder;
    private project: Project;

    constructor() {
        this.projectBuilder = new ProjectBuilder();
    }

    public setText(text: Array<string>): void {
        this.text = text;
    }

    public getText(): Array<string> {
        return this.text;
    }

    public getClient(): string {
        return this.client.getName();
    }

    public getTemplate(): Record<string, unknown> {
        return this.template;
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

    private searchValueInText(identifier: string, type: string, range?: string): string | undefined {
        let index = -1;

        if (type === AttributeType.REGEX) {
            const regexes: Array<RegExp> = identifier.split('&&').map(part => new RegExp(part.trim()));

            // try to match split text
            index = this.text.findIndex((text, idx) => {
                return regexes.every((regex, regexIdx) => {
                    const searchText = this.text[idx + regexIdx];
                    return searchText && regex.test(searchText);
                });
            });
        } else if (type === AttributeType.STRING) {
            index = this.text.findIndex(text => text.toLowerCase().includes(identifier.toLowerCase()));
        }

        if (index === -1) {
            return undefined;
        }

        if (range) {
            const [startOffset, endOffset] = typeof range === 'string' && range.includes('|')
                ? range.split('|').map(offset => offset === 'X' ? (offset === range.split('|')[0] ? 0 : this.text.length - 1) : Number(offset))
                : [Number(range), Number(range)];
            const startIndex = index + startOffset;
            const endIndex = index + endOffset + 1;
            return this.text.slice(Math.max(0, startIndex), Math.min(this.text.length, endIndex)).join(' ');
        }

        return this.text[index];
    }

    private processFStringAttribute(name: string, identifier: string, ): void {
        const matches = identifier.match(/\{(\w+)}/g);
        if (matches) {
            // TODO check if this is double building with other parts of the code
            const currentProject: Project = this.projectBuilder.build();
            let value = identifier;
            matches.forEach(match => {
                const key = match.replace(/[{}]/g, '');
                const attributeValue = currentProject.getAttributeValue(key);
                if (attributeValue) {
                    value = value.replace(match, attributeValue);
                }
            });
            this.setValue(name, value);
        }
    }

    private setValue(name: string, value: string, capitalize = false): void {
        const finalValue = capitalize ? value.charAt(0).toUpperCase() + value.slice(1).toLowerCase() : value;
        // TODO refactor this to more type save changes
        this.projectBuilder = (this.projectBuilder as any)[`set${name.charAt(0).toUpperCase() + name.slice(1)}`](finalValue);
    }

    public async fetchProjectAttributes(): Promise<boolean> {
        const identifiers = this.client.getAttributeIdentifiers();

        identifiers.forEach(attribute => {
            let value = this.searchValueInText(
                attribute.getIdentifier(),
                attribute.getType(),
                attribute.getRange()
            );

            if (!value) return;

            const name = attribute.getName();

            // If a format regex is defined, extract the first substring that matches
            if (attribute.format) {
                const regex = new RegExp(attribute.format);
                const match = value.match(regex);

                if (match) {
                    value = match[0]; // keep only the part that matches the format
                }
            }

            this.setValue(name, value, true);
        });
        identifiers.forEach(attribute => {
            if (attribute.getType() === AttributeType.FORMATTEDSTRING) {
                this.processFStringAttribute(attribute.getName(), attribute.getIdentifier());
            }
        });
        return true;
    }

    public async fillTemplate(): Promise<boolean> {
        const project: Project = this.projectBuilder.build();
        this.project = project;

        for (const key in this.template) {
            if (Object.prototype.hasOwnProperty.call(this.template, key)) {
                const newValue = project.getAttributeValue(key);
                if (newValue !== undefined) {
                    this.template[key] = newValue;
                }
            }
        }

        // TODO set customAttributes better in Project class and ProjectBuilder to be able to write it like the other attributes
        const customAttributes = project.getCustomAttributeValues();
        if (
            Array.isArray(customAttributes) &&
            Array.isArray(this.template.customAttributeValues)
        ) {
            this.template.customAttributeValues.forEach((entry, index) => {
                if (index < customAttributes.length && customAttributes[index] !== undefined) {
                    entry.value = customAttributes[index];
                }
            });
        }

        return true;
    }

    public async createLog(logs: Array<LogLine>, file: File): Promise<boolean> {
        const messages = logs.map(log => log.getMessage());
        const arrayBuffer = await file.arrayBuffer();
        return window.electron.createLog(messages, this.text, this.template, arrayBuffer, JSON.stringify(this.project, null, 2));
    }

}