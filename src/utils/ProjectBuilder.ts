import Project from '../entity/Project';

class ProjectBuilder {
    private project: Project;

    constructor() {
        this.project = new Project();
    }

    public setId(id: number): ProjectBuilder {
        this.project.setId(id);
        return this;
    }

    public setName(name: string): ProjectBuilder {
        this.project.setName(name);
        return this;
    }

    public setStreetName(streetName: string): ProjectBuilder {
        this.project.setStreetName(streetName);
        return this;
    }

    public setHouseNumber(houseNumber: string): ProjectBuilder {
        this.project.setHouseNumber(houseNumber);
        return this;
    }

    public setZipCode(zipCode: string): ProjectBuilder {
        this.project.setZipCode(zipCode);
        return this;
    }

    public setCity(city: string): ProjectBuilder {
        this.project.setCity(city);
        return this;
    }

    public setInformation(information: string): ProjectBuilder {
        this.project.setInformation(information);
        return this;
    }

    public setPhone(phoneNumber: string): ProjectBuilder {
        this.project.setPhone(phoneNumber);
        return this;
    }

    public setEmail(email: string): ProjectBuilder {
        this.project.setEmail(email);
        return this;
    }

    public setReference(reference: string): ProjectBuilder {
        this.project.setReference(reference);
        return this;
    }

    public build(): Project {
        return this.project.build();
    }
}

export default ProjectBuilder;