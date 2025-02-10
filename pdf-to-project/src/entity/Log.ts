export class Log {
  private readonly message: string;
    private readonly type: "info" | "error" | "success" | "warn";

  constructor(message: string, type: "info" | "error" | "success" | "warn") {
    this.message = message;
    this.type = type;
  }

  public getMessage(): string {
    return this.message;
  }

  public getType(): "info" | "error" | "success" | "warn" {
    return this.type;
  }
}