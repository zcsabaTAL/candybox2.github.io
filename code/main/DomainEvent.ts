interface DomainEvent{
    type: string;
    occurredAt: number;
    payload?: any;
}
