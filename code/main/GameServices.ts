///<reference path="Game.ts"/>

class GameServices implements Disposable{
    public events: DomainEventBus;
    private game: Game;
    private disposed: boolean = false;

    constructor(game: Game){
        this.game = game;
        this.events = new DomainEventBus();
    }

    public dispose(): void{
        if(this.disposed) return;
        this.disposed = true;
        this.events.dispose();
        this.game = null;
    }

    public isDisposed(): boolean{
        return this.disposed;
    }
}
