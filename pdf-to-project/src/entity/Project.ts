class Project {
    private readonly id: number;
    private readonly name: string;
    constructor(data: any) {
        this.id = data.id;
        this.name = data.name;
    }

    public getId(): number {
        return this.id;
    }

    public getName() {
        return this.name;
    }
}
export default Project;