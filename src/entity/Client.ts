import {AttributeIdentifier} from "@/entity/AttributeIdentifier";

export default class Client {
    private name: string;
    private abbreviation: string;
    private identifier: string;
    private attributeIdentifiers: Array<AttributeIdentifier>;

    constructor(name: string, abbreviation: string, identifier: string, attributeIdentifiers: Record<string, {identifier: string, type: AttributeType, range: string, format: string}>) {
        this.name = name;
        this.abbreviation = abbreviation;
        this.identifier = identifier;
        this.attributeIdentifiers = Object.keys(attributeIdentifiers).map(key => {
            const attr = attributeIdentifiers[key];
            return new AttributeIdentifier(key, attr.identifier, attr.type, attr.range, attr.format);
        });
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

    public getAttributeIdentifiers(): Array<AttributeIdentifier> {
        return this.attributeIdentifiers;
    }
}