// The first step of the "painted world objects" reskin (replacing individual ascii set
// pieces -- the well, the mill, the pond, etc. -- with actual painted art, one place at a
// time, while everything else on the screen keeps working exactly as before: the real
// buttons/selects/speech are still the same engine-rendered, absolutely-positioned elements
// they always were -- see .asciiRealButton/.asciiSelect in design.css, which already carry
// their own explicit background/color rather than inheriting from the ascii grid, so they
// stay fully visible and functional regardless of what's drawn under them).
//
// Same pattern as PlaceAmbience: build every object's DOM element once at startup and leave
// it in the document for the page's whole lifetime; design.css does the actual showing/
// hiding, keyed off body[data-place="..."] (set by UIBridge). No per-place-change JS, no
// syncing with the screen's periodic redraw.
class WorldObjectLayer {
    private static initialized: boolean = false;

    // One entry per painted object. `id` becomes the element's id (and the CSS hook);
    // `container` is where it gets appended -- #original-game-container so it shares
    // #mainContent's positioning context (that container is `position: relative`, see
    // design.css) and its coordinates line up with the ascii grid underneath it.
    // `motes`: how many small floating "ether spark" spans (see PlaceAmbience.ts's embers,
    // same idea, just scoped to this one object instead of the whole screen) to give it. 0
    // for none.
    private static OBJECTS: { id: string; motes: number }[] = [
        { id: "world-object-wishingwell", motes: 4 },
        { id: "world-object-mill", motes: 3 }
    ];

    public static init(): void {
        if (WorldObjectLayer.initialized) return;
        WorldObjectLayer.initialized = true;

        var container: HTMLElement = document.getElementById("original-game-container");
        if (!container) return;

        for (var i = 0; i < WorldObjectLayer.OBJECTS.length; i++) {
            var def = WorldObjectLayer.OBJECTS[i];
            var el: HTMLElement = document.createElement("div");
            el.id = def.id;
            container.appendChild(el);

            for (var m = 0; m < def.motes; m++) {
                var mote: HTMLElement = document.createElement("span");
                mote.className = "world-object-mote";
                el.appendChild(mote);
            }
        }
    }
}
