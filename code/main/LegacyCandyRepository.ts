///<reference path="CandyRepository.ts"/>
///<reference path="Candies.ts"/>
///<reference path="CandiesEaten.ts"/>

class LegacyCandyRepository implements CandyRepository{
    private candies: Candies;
    private candiesEaten: CandiesEaten;
    private disposed: boolean = false;

    constructor(candies: Candies, candiesEaten: CandiesEaten){
        this.candies = candies;
        this.candiesEaten = candiesEaten;
    }

    public getBalance(): number{
        if(this.disposed) return 0;
        return this.candies.getCurrent();
    }

    public grant(amount: number): boolean{
        if(this.disposed) return false;
        return this.candies.add(amount);
    }

    public spend(amount: number): boolean{
        if(this.disposed) return false;
        return this.candies.add(-amount);
    }

    public eatAll(): boolean{
        if(this.disposed || this.candies.getCurrent() <= 0) return false;
        return this.candies.transferTo(this.candiesEaten);
    }

    public dispose(): void{
        if(this.disposed) return;
        this.disposed = true;
        this.candies = null;
        this.candiesEaten = null;
    }

    public isDisposed(): boolean{
        return this.disposed;
    }
}
