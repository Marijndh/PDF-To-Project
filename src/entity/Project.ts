class Project {
    private id: number;
    private name: string;
    private streetName: string;
    private houseNumber: string;
    private zipCode: string;
    private city: string;
    private information: string;
    private customAttributeValues: Array<string> = [];
    private reference: string;

    constructor() {}

    public setId(id: number): Project {
        this.id = id;
        return this;
    }

    public setName(name: string): Project {
        this.name = name;
        return this;
    }

    public setStreetName(streetName: string): Project {
        this.streetName = streetName;
        return this;
    }

    public setHouseNumber(houseNumber: string): Project {
        this.houseNumber = houseNumber;
        return this;
    }

    public setZipCode(zipCode: string): Project {
        this.zipCode = zipCode;
        return this;
    }

    public setCity(city: string): Project {
        this.city = city;
        return this;
    }

    public setInformation(information: string): Project {
        this.information = information;
        return this;
    }

    public setPhone(phoneNumber: string): Project {
        this.customAttributeValues[0] = phoneNumber;
        return this;
    }

    public setEmail(email: string): Project {
        this.customAttributeValues[1] = email;
        return this;
    }

    public setReference(reference: string): Project {
        this.reference = reference;
        return this;
    }

    public build(): Project {
        return this;
    }

    public getName(): string {
        return this.name;
    }

    public getId(): number {
        return this.id;
    }
    public getAttributeValue(attribute: string): string | undefined {
        switch (attribute) {
            case 'id':
                return String(this.id);
            case 'name':
                return this.name;
            case 'streetName':
                return this.streetName;
            case 'houseNumber':
                return this.houseNumber;
            case 'zipCode':
                return this.zipCode;
            case 'city':
                return this.city;
            case 'information':
                return this.information;
            case 'phone':
                return this.customAttributeValues[0];
            case 'email':
                return this.customAttributeValues[1];
            case 'reference':
                return this.reference;
            default:
                return undefined;
        }
    }
}
export default Project;