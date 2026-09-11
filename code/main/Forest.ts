///<reference path="Quest.ts"/>

class Forest extends Quest{
    // Various timers related to monsters handling
    private timeSinceLastWolfAdding: number = 0;
    private timeSinceLastTreeSpiritAdding: number = 40;
    
    // The ground y position
    private groundYPosition: number = 20;
    
    // How many columns are visible on screen at once -- the rest of the 294-wide forest
    // scrolls in/out as the player moves (see calcNewGlobalDrawingOffset()).
    private viewportWidth: number = 140;
    
    // The mosquito timer (mosquitos will come when the timer reaches 0)
    private mosquitoTimer: number = 250;
    
    // Constructor
    constructor(game: Game){
        super(game);
        
        // Resize the quest
        // The forest is 294 columns wide (see thePlayerWon()'s win-at-x>=294 check), but the
        // *visible* window is much narrower -- forcing the real quest size wider than the
        // drawing size (same trick TheHole uses for its vertical scroll) turns on a horizontal
        // "camera" via globalDrawingOffset.x: see calcNewGlobalDrawingOffset() below.
        this.resizeQuest(this.viewportWidth, this.groundYPosition + 2, new Pos(294, this.groundYPosition + 2));
        
        // Add collision boxes around
        this.addPlayerCollisionBoxes(true, false, true, true);
        
        // Add the player
        this.getGame().getPlayer().loadCandyBoxCharacter(this);
        this.getGame().getPlayer().setGlobalPosition(new Pos(0, this.groundYPosition));
        this.configPlayerOrClone(this.getGame().getPlayer());
        this.addEntity(this.getGame().getPlayer());
        
        // Add the ground
        this.addGround();
        
        // We add some wolves
        for(var i = 0; i < 10; i++){
            this.addWolf(Random.between(80, 280));
        }
        
        // Add the message
        this.getGame().getQuestLog().addMessage(new QuestLogMessage("You enter the forest."));
    }
    
    // Public methods
    public castPlayerTeleport(): void{
        super.castPlayerTeleport(new Pos(0, this.groundYPosition), new Pos(10, 1));
    }
    
    public getGap(): number{
        // The base Quest.getGap() shifts the *whole* rendered block sideways (via a CSS
        // "left" the modern layout doesn't actually honor -- see design.css's #mainContent
        // note) to keep a wide, non-scrolling quest's player roughly centered. Forest no longer
        // needs that: calcNewGlobalDrawingOffset() already keeps the player in view by scrolling
        // the 294-wide level *within* the render area itself, so we opt out here to avoid the
        // two mechanisms fighting (getGap()'s formula assumes the old, unscrolled full-width
        // render area and would badly overshoot against our narrower one).
        return 0;
    }
    
    public configPlayerOrClone(entity: QuestEntity): void{
        entity.setQuestEntityMovement(new QuestEntityMovement(new Pos(1, 0)));
        entity.getQuestEntityMovement().setGravity(true);
        entity.getQuestEntityMovement().setWormsLike(false);
    }
    
    public endQuest(win: boolean): void{
        // We add some messages
        if(win){
            this.getGame().getQuestLog().addMessage(new QuestLogMessage("You made your way through the forest!"));
            Saving.saveBool("mainMapDoneForest", true); // The desert is done
        }
        else{
            this.getGame().getQuestLog().addMessage(new QuestLogMessage("You died in the forest. The tree's leaves should soon be covering your body."));
        }
        
        // We call the endQuest method of our mother class
        super.endQuest(win);
    }
    
    public update(): void{
        if(this.getQuestEnded() == false){
            // Test if the player won the quest, if so, end the quest and return
            if(this.thePlayerWon()){
                this.endQuest(true);
                return;
            }
            
            // Test if the player is dead, if so, end the quest and return
            if(this.getGame().getPlayer().shouldDie()){
                this.endQuest(false);
                return;
            }
            
            // Monsters handling
            this.monstersHandling();
            
            // Update entities
            this.updateEntities();
        }
        
        // Keep the camera centered (with a dead zone) on the player before drawing anything,
        // so the background tiles and every entity -- which already read globalDrawingOffset
        // in their own draw() -- line up for this frame.
        this.calcNewGlobalDrawingOffset();
        
        // Draw
        this.preDraw();
        this.getRenderArea().drawArray(Database.getAscii("places/quests/forest/background"), this.getRealQuestPosition().x + this.getGlobalDrawingOffset().x, this.getRealQuestPosition().y);
        this.getRenderArea().drawArray(Database.getAscii("places/quests/forest/background"), this.getRealQuestPosition().x + this.getGlobalDrawingOffset().x + 98, this.getRealQuestPosition().y);
        this.getRenderArea().drawArray(Database.getAscii("places/quests/forest/background"), this.getRealQuestPosition().x + this.getGlobalDrawingOffset().x + 98*2, this.getRealQuestPosition().y);
        this.drawEntities();
        this.drawAroundQuest();
        if(this.getQuestEnded() == false) this.addExitQuestButton(new CallbackCollection(this.getGame().goToMainMap.bind(this.getGame())), "buttonExitQuestNoKeeping");
        else if(this.getQuestEndedAndWeWon() == false) this.addExitQuestButton(new CallbackCollection(this.getGame().goToMainMap.bind(this.getGame())), "buttonExitQuestNoKeepingBecauseLose");
        else this.addExitQuestButton(new CallbackCollection(this.getGame().goToMainMap.bind(this.getGame())), "buttonExitQuestKeeping");
        this.postDraw();
    }
    
    // Private methods
    private calcNewGlobalDrawingOffset(): void{
        // Dead zone: as long as the player stays within this middle band of the viewport, the
        // camera doesn't move at all (avoids jittery scrolling on every single step). The band
        // is shifted slightly ahead of center so upcoming monsters (which the player mostly
        // walks into, moving right) are visible sooner rather than appearing right at the edge.
        var leftEdge: number = Math.floor(this.viewportWidth * 0.35);
        var rightEdge: number = Math.floor(this.viewportWidth * 0.65);
        var playerX: number = this.getGame().getPlayer().getGlobalPosition().x;
        var offsetX: number = this.getGlobalDrawingOffset().x;
        
        if(playerX + offsetX > rightEdge)
            offsetX = -playerX + rightEdge;
        else if(playerX + offsetX < leftEdge)
            offsetX = -playerX + leftEdge;
        
        // Never scroll past either end of the level -- the start (offset 0) or the point where
        // the last column of the 294-wide level lines up with the right edge of the viewport.
        var minOffsetX: number = Math.min(0, -(294 - this.viewportWidth));
        if(offsetX > 0) offsetX = 0;
        if(offsetX < minOffsetX) offsetX = minOffsetX;
        
        this.setGlobalDrawingOffset(new Pos(offsetX, 0));
    }
    
    private addGround(): void{
        var ground: Wall = new Wall(this, new Pos(0, 0));
        ground.addBox(new Pos(0, this.groundYPosition+1), new Pos(350, 1));
        this.addEntity(ground);
    }
    
    private addMosquito(): boolean{
        return this.addEntity(new Mosquito(this, new Pos(0, this.groundYPosition-Random.between(3, 7)), this.groundYPosition));
    }
    
    private addTreeSpirit(xPosition: number = 294): boolean{ // By default the wolf will be added at the end of the forest
        var treeSpirit: QuestEntity = new TreeSpirit(this, new Pos(xPosition, this.groundYPosition-4), this.groundYPosition);
        treeSpirit.setHealthBar(new QuestEntityHealthBar(treeSpirit, new Pos(5, 1)));
        return this.addEntity(treeSpirit);
    }
    
    private addWolf(xPosition: number = 294): boolean{ // By default the wolf will be added at the end of the forest
        var wolf: QuestEntity = new Wolf(this, new Pos(xPosition, this.groundYPosition-2));
        wolf.setHealthBar(new QuestEntityHealthBar(wolf, new Pos(7, 1)));
        return this.addEntity(wolf);
    }
    
    private monstersHandling(): void{
        // If it's time to add a tree spirit
        if(this.timeSinceLastTreeSpiritAdding > 70 && Random.flipACoin()){
            this.addTreeSpirit(); // We add it
            this.timeSinceLastTreeSpiritAdding = 0; // We reset the timer
        }
        else
            this.timeSinceLastTreeSpiritAdding += 1; // We increase the timer
        
        // If it's time to add a wolf
        if(this.timeSinceLastWolfAdding > 30 && Random.oneChanceOutOf(5)){
            this.addWolf(); // We add it
            this.timeSinceLastWolfAdding = 0; // We reset the timer
        }
        // Else, it's not the time yet
        else
            this.timeSinceLastWolfAdding += 1; // We increase the timer
            
        // If it's time to add a mosquito
        if(this.mosquitoTimer <= 0){
            this.addMosquito();
            this.mosquitoTimer = Random.between(5, 10);
        }
        else this.mosquitoTimer -= 1;
    }
    
    private thePlayerWon(): boolean{
        // If the player is at the right of the desert, we return true
        if(this.getGame().getPlayer().getGlobalPosition().x >= 294)
            return true;
        
        // Else we return false
        return false;
    }
}
