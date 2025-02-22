import { LogLine } from "@/entity/LogLine";

export default class Step {
    private name: string;
    private stepFunction: () => Promise<boolean>;
    private successLog: LogLine;
    private errorLog: LogLine;

    constructor(name: string, stepFunction: () => Promise<boolean>, logMessages: Array<LogLine>) {
        this.name = name;
        this.stepFunction = stepFunction;
        this.successLog = logMessages[0];
        this.errorLog = logMessages[1];
    }

    public async execute(): Promise<boolean> {
        return this.stepFunction();
    }

    public getName(): string {
        return this.name;
    }

    public getSuccessLog(): LogLine {
        return this.successLog;
    }

    public getErrorLog(): LogLine {
        return this.errorLog;
    }
}