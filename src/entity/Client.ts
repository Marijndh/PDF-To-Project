export default class Client {
    private name: string;
    private abbreviation: string;
    private identifier: string;
    private attributeIdentifiers: Record<string, unknown>;

    constructor(name: string, abbreviation: string, identifier: string, attributeIdentifiers: Record<string, unknown>) {
        this.name = name;
        this.abbreviation = abbreviation;
        this.identifier = identifier;
        this.attributeIdentifiers = attributeIdentifiers;
    }

    public getName(): string {
        return this.name;
    }

    public getAbbreviation(): string {
        return this.abbreviation;
    }

    public getIdentifier(): string {
        return this.identifier;
    }

    public getAttributeIdentifiers(): Record<string, unknown> {
        return this.attributeIdentifiers;
    }
}