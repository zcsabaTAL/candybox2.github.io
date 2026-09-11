///<reference path="GridItem.ts"/>

class UnicornHorn extends GridItem{
    public getSpecialAbility(): string{
        return "Regularly heals you during quests (unicorn horn).";
    }
    
    public update(player: Player, quest: Quest): void{
        player.heal(3);
    }
}