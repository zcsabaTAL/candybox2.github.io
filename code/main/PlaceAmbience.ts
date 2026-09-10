// Builds a small set of floating "ember" motes once at startup and leaves them running in
// the background for the lifetime of the page. The container and every ember span live in
// the DOM at all times, but design.css hides the whole thing (display: none) unless the
// current place is one of the reskinned ones (currently Village and MainMap, matched via
// body[data-place="..."], set by UIBridge) -- so this never does anything visible, or costs
// anything to render, on any other screen. Originally written just for the Village pilot
// (hence "ember" rather than a more generic name) and generalized here once the Map screen
// got the same treatment -- one shared, always-running particle layer, with per-place CSS
// deciding whether (and in what color) it shows.
//
// Built this way (create once, toggle purely with CSS) rather than creating/destroying
// elements on every place change, to avoid adding yet another thing that has to stay in
// sync with a screen's periodic redraw (see AsciiGroupHover's own comment about that redraw
// for the history of bugs that pattern has caused here).
class PlaceAmbience {
    private static initialized: boolean = false;
    private static EMBER_COUNT: number = 7;

    public static init(): void {
        if (PlaceAmbience.initialized) return;
        PlaceAmbience.initialized = true;

        var container: HTMLElement = document.createElement("div");
        container.id = "place-ambience";

        for (var i = 0; i < PlaceAmbience.EMBER_COUNT; i++) {
            var ember: HTMLElement = document.createElement("span");
            ember.className = "place-ember";

            // Spread embers across the width, and stagger their timing/duration/drift so
            // they don't all move in obvious lockstep.
            var left: number = Math.round((i / PlaceAmbience.EMBER_COUNT) * 100 + (Math.random() * 10 - 5));
            var duration: number = 9 + Math.random() * 7; // 9s - 16s
            var delay: number = Math.random() * duration * -1; // negative delay so they start mid-cycle, already spread out
            var drift: number = Math.round(Math.random() * 40 - 20); // -20px .. 20px horizontal drift

            ember.style.left = left + "%";
            ember.style.animationDuration = duration + "s";
            ember.style.animationDelay = delay + "s";
            (<any>ember.style)["--ember-drift"] = drift + "px";

            container.appendChild(ember);
        }

        document.body.appendChild(container);
    }
}
