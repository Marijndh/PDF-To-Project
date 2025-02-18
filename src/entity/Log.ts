export type LogType = "info" | "error" | "success" | "warning";

export class Log {
  private readonly message: string;
  private readonly type: LogType;

  constructor(type: string, message: string) {
    this.message = message;
    this.type = ["info", "error", "success", "warning"].includes(type) ? (type as LogType) : "info";
  }

  public getMessage(): string {
    return this.message;
  }

  public getType(): LogType {
    return this.type;
  }
}