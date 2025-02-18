import { Log } from "@/entity/Log";

export default class Step {
    private name: string;
    private stepFunction: () => Promise<boolean>;
    private successLog: Log;
    private errorLog: Log;

    constructor(name: string, stepFunction: () => Promise<boolean>, logMessages: Array<Log>) {
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

    public getSuccessLog(): Log {
        return this.successLog;
    }

    public getErrorLog(): Log {
        return this.errorLog;
    }
}