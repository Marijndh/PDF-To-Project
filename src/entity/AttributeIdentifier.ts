import {AttributeType} from "@/enums/AttributeType";

export class AttributeIdentifier {
    name: string;
    identifier: string;
    range?: string;
    type: AttributeType;
    format?: string;
    value: string;

    constructor(name: string, identifier: string, type: AttributeType, range?: string, format?: string) {
        this.name = name;
        this.identifier = identifier;
        this.type = type;
        this.range = range;
        this.format = format;
    }

    public setValue(value: string): void {
            this.value = value;
    }

    public isFound(): boolean {
        return this.value === undefined;
    }

    public getIdentifier(): string {
       return this.identifier;
    }

    public getType(): string {
       return this.type;
    }

    public getRange(): string | undefined {
       return this.range;
    }

    public getName(): string {
        return this.name;
    }

    public getFormat(): string | undefined {
        return this.format;
    }
}