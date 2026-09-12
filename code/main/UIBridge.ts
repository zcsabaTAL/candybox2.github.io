class UIBridge {
    // Only one UIBridge should ever be actively ticking at a time. If a new one is created while an
    // older one is still running (e.g. "Load from file" rebuilds the Game), we stop the old loop so
    // two loops never fight over the same DOM elements (which would look like constant flickering).
    private static currentInstance: UIBridge = null;
    
    // Definitions for the modern nav tabs, mirroring StatusBar.ts's addTab() calls: which Saving bool
    // gates the tab, what place class name means "this tab is active", the label, and which Game
    // method to call to navigate there.
    private static TAB_DEFS: any[] = [
        { flag: "statusBarUnlocked", place: "CandyBox", label: "THE CANDY BOX", go: "goToCandyBox" },
        { flag: "statusBarUnlockedInventory", place: "Inventory", label: "INVENTORY", go: "goToInventory" },
        { flag: "statusBarUnlockedMap", place: "MainMap", label: "MAP", go: "goToMap" },
        { flag: "statusBarUnlockedLollipopFarm", place: "LollipopFarm", label: "LOLLIPOP FARM", go: "goToLollipopFarm" },
        { flag: "statusBarUnlockedCauldron", place: "Cauldron", label: "THE CAULDRON", go: "goToCauldron" },
        { flag: "statusBarUnlockedInsideYourBox", place: "InsideYourBox", label: "INSIDE YOUR BOX", go: "goToInsideYourBox" },
        { flag: "statusBarUnlockedTheComputer", place: "TheComputer", label: "THE COMPUTER", go: "goToTheComputer" },
        { flag: "statusBarUnlockedTheArena", place: "TheArena", label: "THE ARENA", go: "goToTheArena" },
        { flag: "statusBarUnlockedSave", place: "Save", label: "SAVE", go: "goToSave" },
        { flag: "statusBarUnlockedCfg", place: "Cfg", label: "SETTINGS", go: "goToCfg" }
    ];
    
    // Called from the onclick="" of the generated nav buttons (they can't close over `this`).
    public static navigate(goMethodName: string): void {
        if (!UIBridge.currentInstance) return;
        var game: any = UIBridge.currentInstance.game;
        if (typeof game[goMethodName] === "function") game[goMethodName]();
    }
    
    private game: Game;
    private lastPlaceName: string = "";
    private lastNavSignature: string = "";
    private lastQuestLogSignature: string = "";
    private disposed: boolean = false;
    
    constructor(game: Game) {
        if (UIBridge.currentInstance) {
            UIBridge.currentInstance.dispose();
        }
        UIBridge.currentInstance = this;
        
        this.game = game;
        this.updateLoop();
    }
    
    public dispose(): void {
        this.disposed = true;
        var logContainer = document.getElementById("ui-quest-log");
        if (logContainer) {
            logContainer.style.display = "none";
            logContainer.innerHTML = "";
        }
        this.lastQuestLogSignature = "";
    }
    
    private updateLoop() {
        if (this.disposed) return;
        
        this.updateStats();
        this.updateHeaders();
        this.updateNav();
        this.updateHealthBar();
        this.updateQuestLog();
        setTimeout(this.updateLoop.bind(this), 100);
    }
    
    private updateHeaders() {
        // Access place dynamically since it's private in Game
        var currentPlace: any = this.game['place'];
        var currentPlaceName = currentPlace ? currentPlace.constructor.name : "";
        
        // Prevent continuous DOM updates if the place hasn't changed
        if (currentPlaceName !== this.lastPlaceName) {
            this.lastPlaceName = currentPlaceName;
            
            // Exposes the current place name on <body data-place="..."> so CSS (and other
            // scripts) can scope a visual treatment to one specific place -- e.g. the
            // Village's cool-toned ascii reskin -- without touching every other screen.
            document.body.setAttribute("data-place", currentPlaceName);

            // Switch background music to match: place-specific track if one exists, else the
            // fight theme on any quest/combat screen, else the main theme everywhere else.
            if (typeof MusicBridge !== "undefined") {
                MusicBridge.setPlace(currentPlaceName, currentPlace instanceof Quest);
            }
            if (typeof VoiceBridge !== "undefined") {
                VoiceBridge.setPlace(currentPlaceName);
            }
            
            var titleEl = document.getElementById("ui-place-title");
            var subtitleEl = document.getElementById("ui-place-subtitle");
            var flavorEl = document.getElementById("ui-place-flavor");
            
            if (titleEl && subtitleEl) {
                var subtitle = "&laquo; <span class=\"highlight\">THE CANDY BOX</span> &raquo;";
                var title = "";
                // Italic mood line under the title. Empty/hidden by default -- only specific
                // places (currently just the Village pilot) set one.
                var flavor = "";
                
                switch (currentPlaceName) {
                    case "CandyBox":
                        title = "A STRANGE BOX<br>PRODUCING SWEETS.";
                        flavor = "&ldquo;No one quite recalls when the box first began to give.&rdquo;";
                        break;
                    case "Inventory":
                        title = "INVENTORY";
                        break;
                    case "Cfg":
                        title = "CONFIGURATION";
                        break;
                    case "Save":
                        title = "SAVING";
                        break;
                    case "MainMap":
                        subtitle = "&laquo; <span class=\"highlight\">EXPLORATION</span> &raquo;";
                        title = "THE MAP";
                        flavor = "&ldquo;Every road on this map was walked by someone who did not come back to redraw it.&rdquo;";
                        break;
                    case "TheArena":
                        subtitle = "&laquo; <span class=\"highlight\">COMBAT</span> &raquo;";
                        title = "THE ARENA";
                        break;
                    case "LollipopFarm":
                        subtitle = "&laquo; <span class=\"highlight\">PRODUCTION</span> &raquo;";
                        title = "LOLLIPOP FARM";
                        flavor = "&ldquo;Rows of hardened sugar, rooted deep in old, dark soil.&rdquo;";
                        break;
                    case "Cauldron":
                        subtitle = "&laquo; <span class=\"highlight\">MAGIC</span> &raquo;";
                        title = "THE CAULDRON";
                        break;
                    case "Village":
                        title = "VILLAGE";
                        flavor = "&ldquo;A hundred years of woodsmoke and sugar cling to these walls.&rdquo;";
                        break;
                    case "Forge":
                        subtitle = "&laquo; <span class=\"highlight\">THE VILLAGE</span> &raquo;";
                        title = "THE FORGE";
                        flavor = "&ldquo;The rhythmic ring of an anvil echoes off soot-stained timber.&rdquo;";
                        break;
                    case "Dragon":
                        subtitle = "&laquo; <span class=\"highlight\">THE CASTLE</span> &raquo;";
                        title = "THE DRAGON'S LAIR";
                        flavor = "&ldquo;Beneath the mountain's breath, ancient embers still glow in the dark.&rdquo;";
                        break;
                    default:
                        // Convert CamelCase to UPPERCASE SPACE for default
                        if (currentPlaceName) {
                            title = currentPlaceName.replace(/([A-Z])/g, ' $1').trim().toUpperCase();
                        } else {
                            title = "LOADING...";
                        }
                        break;
                }
                
                // Only update innerHTML if it's actually different to prevent layout recalculations/flickering
                if (titleEl.innerHTML !== title) titleEl.innerHTML = title;
                if (subtitleEl.innerHTML !== subtitle) subtitleEl.innerHTML = subtitle;
                if (flavorEl) {
                    if (flavor) {
                        if (flavorEl.innerHTML !== flavor) flavorEl.innerHTML = flavor;
                        flavorEl.style.display = "block";
                    }
                    else {
                        flavorEl.style.display = "none";
                    }
                }
            }
        }
    }
    
    private updateStats() {
        // Candies
        var candiesCount = document.getElementById("ui-candies-count");
        if (candiesCount) {
            var formattedCandies = Algo.numberToStringButNicely(this.game.getCandies().getCurrent());
            if (candiesCount.textContent !== formattedCandies) {
                candiesCount.textContent = formattedCandies;
            }
        }
        
        var candiesRate = document.getElementById("ui-candies-rate");
        if (candiesRate) {
           var p = this.game.getCandies().getAccumulated() > 0 ? (typeof DevMode !== 'undefined' && DevMode.isEnabled ? 100 : 1) : 0; 
           var pStr = p.toString();
           if (candiesRate.textContent !== pStr) {
               candiesRate.textContent = pStr;
           }
        }
        
        // Lollipops
        var lollipopsMax = this.game.getLollipops().getMax();
        var lollipopContainer = document.getElementById("ui-lollipop-container");
        if (lollipopContainer) {
            if (lollipopsMax > 0) {
                if (lollipopContainer.style.display !== "flex") lollipopContainer.style.display = "flex";
                var lollipopsCount = document.getElementById("ui-lollipops-count");
                if (lollipopsCount) {
                    var formattedLollipops = Algo.numberToStringButNicely(this.game.getLollipops().getCurrent());
                    if (lollipopsCount.textContent !== formattedLollipops) {
                        lollipopsCount.textContent = formattedLollipops;
                    }
                }
            } else {
                if (lollipopContainer.style.display !== "none") lollipopContainer.style.display = "none";
            }
        }
        
        // Chocolate bars
        var chocolateMax = this.game.getChocolateBars().getMax();
        var chocolateContainer = document.getElementById("ui-chocolate-container");
        if (chocolateContainer) {
            if (chocolateMax > 0) {
                if (chocolateContainer.style.display !== "flex") chocolateContainer.style.display = "flex";
                var chocolateCount = document.getElementById("ui-chocolate-count");
                if (chocolateCount) {
                    var formattedChocolate = Algo.numberToStringButNicely(this.game.getChocolateBars().getCurrent());
                    if (chocolateCount.textContent !== formattedChocolate) {
                        chocolateCount.textContent = formattedChocolate;
                    }
                }
            } else {
                if (chocolateContainer.style.display !== "none") chocolateContainer.style.display = "none";
            }
        }
        
        // Pains au chocolat
        var painMax = this.game.getPainsAuChocolat().getMax();
        var painContainer = document.getElementById("ui-pain-container");
        if (painContainer) {
            if (painMax > 0) {
                if (painContainer.style.display !== "flex") painContainer.style.display = "flex";
                var painCount = document.getElementById("ui-pain-count");
                if (painCount) {
                    var formattedPain = Algo.numberToStringButNicely(this.game.getPainsAuChocolat().getCurrent());
                    if (painCount.textContent !== formattedPain) {
                        painCount.textContent = formattedPain;
                    }
                }
            } else {
                if (painContainer.style.display !== "none") painContainer.style.display = "none";
            }
        }
    }
    
    private updateNav() {
        var navContainer = document.getElementById("ui-nav-tabs");
        if (!navContainer) return;
        
        var currentPlace: any = this.game['place'];
        var currentPlaceName = currentPlace ? currentPlace.constructor.name : "";
        
        // Build a signature of (current place + every tab's unlocked state) so we only touch the
        // DOM when something actually changed, instead of rebuilding the button list every 100ms.
        var visibleTabs: any[] = [];
        var sigParts: string[] = [currentPlaceName];
        for (var i = 0; i < UIBridge.TAB_DEFS.length; i++) {
            var def = UIBridge.TAB_DEFS[i];
            var unlocked = Saving.loadBool(def.flag);
            sigParts.push(unlocked ? "1" : "0");
            if (unlocked) visibleTabs.push(def);
        }
        var signature = sigParts.join("|");
        
        if (signature === this.lastNavSignature) return;
        this.lastNavSignature = signature;
        
        if (visibleTabs.length === 0) {
            navContainer.style.display = "none";
            return;
        }
        
        navContainer.style.display = "flex";
        
        var html = "";
        for (var j = 0; j < visibleTabs.length; j++) {
            var t = visibleTabs[j];
            var activeClass = (t.place === currentPlaceName) ? " active" : "";
            html += '<button type="button" class="nav-tab' + activeClass + '" onclick="UIBridge.navigate(\'' + t.go + '\')">' + t.label + '</button>';
        }
        navContainer.innerHTML = html;
    }
    
    private updateHealthBar() {
        var container = document.getElementById("ui-health-container");
        if (!container) return;
        
        if (!Saving.loadBool("statusBarUnlockedHealthBar")) {
            if (container.style.display !== "none") container.style.display = "none";
            return;
        }
        if (container.style.display !== "block") container.style.display = "block";
        
        var player = this.game.getPlayer();
        var hp = player.getHp();
        var maxHp = player.getMaxHp();
        var pct = maxHp > 0 ? Math.max(0, Math.min(100, (hp / maxHp) * 100)) : 0;
        
        var fill = document.getElementById("ui-health-fill");
        var fillWidth = pct + "%";
        if (fill && fill.style.width !== fillWidth) fill.style.width = fillWidth;
        
        var text = document.getElementById("ui-health-text");
        var textStr = hp + " / " + maxHp;
        if (text && text.textContent !== textStr) text.textContent = textStr;
    }
    
    private updateQuestLog(): void {
        var container = document.getElementById("ui-quest-log");
        if (!container) return;
        
        var currentPlace: any = this.game['place'];
        var isQuest: boolean = (typeof Quest !== "undefined" && currentPlace instanceof Quest);
        
        if (!isQuest) {
            if (container.style.display !== "none") {
                container.style.display = "none";
                this.lastQuestLogSignature = "";
            }
            return;
        }
        
        if (container.style.display !== "flex") {
            container.style.display = "flex";
        }
        
        var questLog: QuestLog = this.game.getQuestLog();
        var msgCount: number = questLog.getMessageCount();
        
        var lastMsg: QuestLogMessage = msgCount > 0 ? questLog.getMessageAt(msgCount - 1) : null;
        var sig: string = msgCount + "_" + (lastMsg ? (lastMsg.getLeft() + "|" + lastMsg.getRight() + "|" + (lastMsg.isBold() ? "1" : "0")) : "");
        if (sig === this.lastQuestLogSignature) return;
        this.lastQuestLogSignature = sig;
        
        container.innerHTML = "";
        var fragment: DocumentFragment = document.createDocumentFragment();
        for (var i = 0; i < msgCount; i++) {
            var msg: QuestLogMessage = questLog.getMessageAt(i);
            if (!msg) continue;
            var left: string = msg.getLeft() || "";
            var right: string = msg.getRight() || "";
            
            // If this is a delimiter row (starts with "---")
            if (left.indexOf("---") === 0) {
                var divider = document.createElement("div");
                divider.className = "quest-log-divider";
                fragment.appendChild(divider);
                continue;
            }
            
            // Skip purely empty spacer rows
            if (left.length === 0 && right.length === 0) continue;
            
            var row = document.createElement("div");
            row.className = msg.isBold() ? "quest-log-row quest-log-bold" : "quest-log-row";
            
            var textSpan = document.createElement("span");
            textSpan.className = "quest-log-text";
            textSpan.textContent = left;
            row.appendChild(textSpan);
            
            if (right.length > 0) {
                var countSpan = document.createElement("span");
                countSpan.className = "quest-log-count";
                countSpan.textContent = right;
                row.appendChild(countSpan);
            }
            
            fragment.appendChild(row);
        }
        container.appendChild(fragment);
        container.scrollTop = container.scrollHeight;
    }
}

