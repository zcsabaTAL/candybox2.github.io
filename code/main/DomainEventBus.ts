interface DomainEventHandler{
    (event: DomainEvent): void;
}

class DomainEventSubscription implements Disposable{
    private bus: DomainEventBus;
    private handler: DomainEventHandler;
    private disposed: boolean = false;

    constructor(bus: DomainEventBus, handler: DomainEventHandler){
        this.bus = bus;
        this.handler = handler;
    }

    public dispose(): void{
        if(this.disposed) return;
        this.disposed = true;
        this.bus.unsubscribe(this.handler);
        this.bus = null;
        this.handler = null;
    }
}

class DomainEventBus implements Disposable{
    private handlers: DomainEventHandler[] = [];
    private disposed: boolean = false;

    public subscribe(handler: DomainEventHandler): Disposable{
        if(this.disposed) return new DomainEventSubscription(this, handler);
        this.handlers.push(handler);
        return new DomainEventSubscription(this, handler);
    }

    public publish(event: DomainEvent): void{
        if(this.disposed) return;
        var currentHandlers: DomainEventHandler[] = this.handlers.slice(0);
        for(var i: number = 0; i < currentHandlers.length; i++){
            currentHandlers[i](event);
        }
    }

    public unsubscribe(handler: DomainEventHandler): void{
        if(this.disposed) return;
        for(var i: number = this.handlers.length - 1; i >= 0; i--){
            if(this.handlers[i] === handler) this.handlers.splice(i, 1);
        }
    }

    public dispose(): void{
        if(this.disposed) return;
        this.disposed = true;
        this.handlers = [];
    }

    public isDisposed(): boolean{
        return this.disposed;
    }
}
