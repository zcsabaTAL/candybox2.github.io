///<reference path="CandyRepository.ts"/>
///<reference path="CommandResult.ts"/>
///<reference path="DomainEventBus.ts"/>

interface CandyTransactionRecord{
    fingerprint: string;
}

class CandySystem implements Disposable{
    private repository: CandyRepository;
    private events: DomainEventBus;
    private transactions: { [transactionId: string]: CandyTransactionRecord; } = {};
    private disposed: boolean = false;

    constructor(repository: CandyRepository, events: DomainEventBus){
        this.repository = repository;
        this.events = events;
    }

    public getBalance(): number{
        if(this.disposed) return 0;
        return this.repository.getBalance();
    }

    public grant(amount: number, reason: string, transactionId: string): CommandResult{
        var invalid: CommandResult = this.validate(amount, reason, transactionId);
        if(invalid != null) return invalid;

        var fingerprint: string = this.fingerprint("grant", amount, reason);
        var replay: CommandResult = this.checkReplay(transactionId, fingerprint);
        if(replay != null) return replay;

        var previousBalance: number = this.repository.getBalance();
        if(!this.repository.grant(amount)) return this.failure("INVALID_AMOUNT");

        return this.complete(transactionId, fingerprint, {
            type: "candy.granted",
            occurredAt: new Date().getTime(),
            payload: {
                transactionId: transactionId,
                amount: amount,
                reason: reason,
                previousBalance: previousBalance,
                newBalance: this.repository.getBalance()
            }
        });
    }

    public spend(amount: number, reason: string, transactionId: string): CommandResult{
        var invalid: CommandResult = this.validate(amount, reason, transactionId);
        if(invalid != null) return invalid;

        var fingerprint: string = this.fingerprint("spend", amount, reason);
        var replay: CommandResult = this.checkReplay(transactionId, fingerprint);
        if(replay != null) return replay;

        var previousBalance: number = this.repository.getBalance();
        if(previousBalance < amount || !this.repository.spend(amount)) return this.failure("NOT_ENOUGH_CANDIES");

        return this.complete(transactionId, fingerprint, {
            type: "candy.spent",
            occurredAt: new Date().getTime(),
            payload: {
                transactionId: transactionId,
                amount: amount,
                reason: reason,
                previousBalance: previousBalance,
                newBalance: this.repository.getBalance()
            }
        });
    }

    public eatAll(transactionId: string): CommandResult{
        if(this.disposed) return this.failure("RUNTIME_DISPOSED");
        if(!this.isNonEmpty(transactionId)) return this.failure("INVALID_TRANSACTION_ID");

        var fingerprint: string = this.fingerprint("eatAll", null, null);
        var replay: CommandResult = this.checkReplay(transactionId, fingerprint);
        if(replay != null) return replay;

        var previousBalance: number = this.repository.getBalance();
        if(previousBalance <= 0 || !this.repository.eatAll()) return this.failure("NO_CANDIES_TO_EAT");

        return this.complete(transactionId, fingerprint, {
            type: "candy.eaten",
            occurredAt: new Date().getTime(),
            payload: {
                transactionId: transactionId,
                amount: previousBalance,
                previousBalance: previousBalance,
                newBalance: this.repository.getBalance()
            }
        });
    }

    public dispose(): void{
        if(this.disposed) return;
        this.disposed = true;
        this.transactions = {};
        this.repository = null;
        this.events = null;
    }

    public isDisposed(): boolean{
        return this.disposed;
    }

    private validate(amount: number, reason: string, transactionId: string): CommandResult{
        if(this.disposed) return this.failure("RUNTIME_DISPOSED");
        if(typeof amount != "number" || !isFinite(amount) || amount <= 0 || Math.floor(amount) != amount)
            return this.failure("INVALID_AMOUNT");
        if(!this.isNonEmpty(reason)) return this.failure("INVALID_REASON");
        if(!this.isNonEmpty(transactionId)) return this.failure("INVALID_TRANSACTION_ID");
        return null;
    }

    private isNonEmpty(value: string): boolean{
        return typeof value == "string" && value.replace(/^\s+|\s+$/g, "").length > 0;
    }

    private fingerprint(operation: string, amount: number, reason: string): string{
        return operation + "|" + (amount == null ? "" : amount.toString()) + "|" + (reason == null ? "" : reason);
    }

    private checkReplay(transactionId: string, fingerprint: string): CommandResult{
        var existing: CandyTransactionRecord = this.transactions["transaction:" + transactionId];
        if(existing == null) return null;
        if(existing.fingerprint != fingerprint) return this.failure("TRANSACTION_ID_CONFLICT");
        return { ok: true, replayed: true };
    }

    private complete(transactionId: string, fingerprint: string, event: DomainEvent): CommandResult{
        this.transactions["transaction:" + transactionId] = { fingerprint: fingerprint };
        this.events.publish(event);
        return { ok: true, events: [event] };
    }

    private failure(errorCode: string): CommandResult{
        return { ok: false, errorCode: errorCode };
    }
}
