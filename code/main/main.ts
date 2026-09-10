///<reference path="Game.ts"/>
///<reference path="./../../libs/jquery.d.ts"/>

module Main{
    // The game
    var game: Game = null;
    
    // Information about loading
    var loadingType: MainLoadingType = MainLoadingType.NONE;
    var loadingString: string = null;
    
    // Information about the game mode
    var gameMode: string = null;

    // Public functions    
    export function documentIsReady(): void{
        Keyboard.execute(); // Execute the Kayboard jquery stuff
        start(); // Start the game
    }
    
    export function reloadEverythingFromFile(fileContent: string): void{
        // Clear intervals for the current game
        game.clearAllIntervals();
        // Set the loading type
        loadingType = MainLoadingType.FILE;
        // Set the loading string
        loadingString = fileContent;
        // Set the gamemode (null so that it is set from loading)
        gameMode = null;
        // We can't register anymore
        Saving.canRegister = false;
        // Finally start (this will erase the current game)
        start();
    }
    
    // If the url didn't explicitly ask for a slot or a gamemode, silently resume the last slot we saved to or loaded
    // (if local saving is supported and that slot still has data). This only changes the auto-resume behavior on a
    // plain page load; an explicit ?slot=N or ?gamemode=X in the url is never overridden.
    export function autoResumeLastSlotIfNoUrlData(): void{
        if(loadingType != MainLoadingType.NONE) return; // An explicit ?slot= or ?gamemode= already won
        if(!LocalSaving.supportsLocalSaving()) return;
        
        var lastUsedSlotId: string = localStorage.getItem("lastUsedSlotId");
        if(lastUsedSlotId != null && localStorage.getItem(lastUsedSlotId) != null){
            loadingType = MainLoadingType.LOCAL;
            loadingString = lastUsedSlotId;
        }
    }
    
    export function setUrlData(urlData: string): void{
        // If there's nothing in the url, or it doesn't start with "?", there's nothing to parse
        if(urlData == "" || urlData.charAt(0) != "?") return;
        
        // Strip the question mark, then split into individual "key=value" pairs on "&" so that
        // any number of query parameters (in any order) are handled correctly -- not just a single one.
        var pairs: string[] = urlData.substr(1).split("&");
        
        for(var i = 0; i < pairs.length; i++){
            var pair: string = pairs[i];
            var eqIndex: number = pair.indexOf("=");
            
            // Skip pairs without an equal sign, or where the equal sign is the last character
            if(eqIndex == -1 || eqIndex == pair.length - 1) continue;
            
            var beforeEqual: string = pair.substr(0, eqIndex);
            var afterEqual: string = pair.substr(eqIndex + 1);
            
            // Do different things depending on the value of beforeEqual
            switch(beforeEqual){
                // If we're trying to load a local slot
                case "slot":
                    loadingType = MainLoadingType.LOCAL;
                    loadingString = "slot" + afterEqual;
                break;
                // If we're trying to launch a new game with a special mode
                case "gamemode":
                    gameMode = afterEqual;
                break;
            }
        }
    }
    
    function start(): void{
        game = new Game(gameMode);
        Keyboard.setGame(game);
        Saving.load(game, loadingType, loadingString);
        game.postLoad();
        
        // Initialize the custom UI Bridge only now, once the save data (if any) has actually been
        // loaded into the game's resources. Doing this earlier (e.g. inside the Game constructor)
        // means the first tick(s) render zeroed-out / hidden stats, which then suddenly snap to the
        // real loaded values a moment later -- visible as a flash/flicker when loading a save.
        if (typeof UIBridge !== "undefined") new UIBridge(game);
    }
}

$(document).ready(function(){
    // Groups the hover highlight across multi-row ASCII objects (map landmarks, the
    // grimoire in the Sorceress' Hut, etc.) instead of only lighting up the single
    // row/character under the cursor. Independent of game state, so it's safe to set
    // up immediately.
    if (typeof AsciiGroupHover !== "undefined") AsciiGroupHover.init();
    if (typeof PlaceAmbience !== "undefined") PlaceAmbience.init();

    Main.setUrlData(window.location.search);
    Main.autoResumeLastSlotIfNoUrlData();
    Main.documentIsReady();
});