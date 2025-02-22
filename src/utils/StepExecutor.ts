import {LogLine} from "@/entity/LogLine";
import Step from "@/entity/Step";

export default class StepExecutor {
    private steps: Array<Step> = [];
    private currentStep: number;
    private logs: Array<LogLine>;
    private logMessages: Record<string, Array<LogLine>>;

    constructor(logs: Array<LogLine>, currentStep: number) {
        this.logs = logs;
        this.currentStep = currentStep;
    }

    public async initializeLogMessages(): Promise<number> {
        const logJson = await window.electron.getLogMessages();
        this.logMessages = Object.entries(logJson).reduce((acc, [key, value]) => {
            acc[key] = (value as Array<{ type: string; message: string }>).map(
                (log) => new LogLine(log.type, log.message)
            );
            return acc;
        }, {} as Record<string, Array<LogLine>>);

        return Object.keys(this.logMessages).length;
    }

    public getTotalSteps(): number {
        return this.steps.length;
    }

    public getCurrentStep(): number {
        return this.currentStep;
    }

    addStep(name: string, stepFunction: () => Promise<boolean>): void {
        if (this.logMessages[name] && Array.isArray(this.logMessages[name]) && this.logMessages[name].length === 2) {
            this.steps.push(new Step(name, stepFunction, this.logMessages[name]));
        } else {
            this.logs.push(new LogLine("error", `Step ${name} not found in log messages`));
        }
    }

    async runSteps(): Promise<boolean> {
        for (; this.currentStep <= this.steps.length; this.currentStep++) {
            const step: Step = this.steps[this.currentStep - 1];
            try {
                const result = await step.execute();
                if (!result) {
                    this.logs.push(step.getErrorLog());
                    return false;
                } else {
                    this.logs.push(step.getSuccessLog());
                }
            } catch (error) {
                this.logs.push(new LogLine("error", `Step ${this.currentStep} failed with error: ${error.message}`));
                return false;
            }
        }
        return true;
    }
}