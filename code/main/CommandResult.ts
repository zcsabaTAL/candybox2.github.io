interface CommandResult{
    ok: boolean;
    errorCode?: string;
    events?: DomainEvent[];
}
