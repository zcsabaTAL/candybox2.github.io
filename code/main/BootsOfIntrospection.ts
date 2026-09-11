///<reference path="EqItem.ts"/>

class BootsOfIntrospection extends EqItem{
    // Constructor
    constructor(){
        super("eqItemBootsBootsOfIntrospection",
              "eqItemBootsBootsOfIntrospectionName",
              "eqItemBootsBootsOfIntrospectionDescription",
              "eqItems/boots/bootsOfIntrospection");
    }
    
    // Special ability
    public getSpecialAbility(): string{
        return "You do not move while touching the ground (boots of introspection).";
    }
}