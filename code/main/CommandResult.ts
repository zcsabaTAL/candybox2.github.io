interface Disposable{
    dispose(): void;
}

interface DomainEvent{
    type: string;
    occurredAt: number;
    payload?: any;
}

interface CommandResult{
    ok: boolean;
    errorCode?: string;
    events?: DomainEvent[];
}
