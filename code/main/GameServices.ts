///<reference path="Game.ts"/>
///<reference path="CandySystem.ts"/>
///<reference path="LegacyCandyRepository.ts"/>

class GameServices implements Disposable{
    public events: DomainEventBus;
    public candies: CandySystem;
    private game: Game;
    private candyRepository: LegacyCandyRepository;
    private disposed: boolean = false;

    constructor(game: Game){
        this.game = game;
        this.events = new DomainEventBus();
        this.candyRepository = new LegacyCandyRepository(game.getCandies(), game.getCandiesEaten());
        this.candies = new CandySystem(this.candyRepository, this.events);
    }

    public dispose(): void{
        if(this.disposed) return;
        this.disposed = true;
        this.candies.dispose();
        this.candyRepository.dispose();
        this.events.dispose();
        this.candies = null;
        this.candyRepository = null;
        this.game = null;
    }

    public isDisposed(): boolean{
        return this.disposed;
    }
}
