///<reference path="GridItem.ts"/>

class XinopherydonClaw extends GridItem{
    public getSpecialAbility(): string{
        return "Inflicted damage multiplied by 2 (xinopherydon claw).";
    }
    
    public hit(player: Player, quest: Quest, questEntity: QuestEntity, damage: number, reason: QuestEntityDamageReason): number{
        return damage*2;
    }
}