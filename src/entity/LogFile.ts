class LogFile {
    private readonly name: string;
    private readonly path: string;
    constructor(name: string, path: string) {
        this.path = path;
        this.name = name;
    }

    public getName(): string {
        return this.name;
    }

    public getPath(): string {
        return this.path;
    }
}
export default LogFile;