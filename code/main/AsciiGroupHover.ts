// Several places in the game draw one logical ASCII "object" (a map landmark, the
// grimoire on the shelf in the Sorceress' Hut, etc.) as MULTIPLE separate rows, each
// wrapped in its own <span class="asciiButton someSharedClass">...</span> by
// RenderArea.addAsciiButton(). All the rows of one object already share that second
// class name -- but the native CSS :hover pseudo-class only ever colors the exact
// <span> the mouse is over, so hovering such a multi-row object used to highlight a
// single row/character while the rest of the object stayed the default color.
//
// This class fixes that generically, for every current and future ASCII object built
// this way, without touching how any of them are drawn: on hover of any .asciiButton,
// it finds every other .asciiButton sharing the same second class and highlights them
// together via a shared CSS class (see .asciiGroupHover in design.css), and shows a
// companion glow marker (AsciiPoiMarker) over the group.
//
// It listens on the CAPTURE phase rather than delegating through jQuery's normal
// (bubble-phase) event binding. Several of these ascii buttons already have their own
// mouseover/mouseout handler that returns false (e.g. RenderLinkOnHoverShowTooltip, for
// the ascii tooltips), which stops the event from bubbling any further -- a bubble-phase
// listener on document would simply never see those events. A capture-phase listener
// always runs first, before any of that, so it isn't affected.
//
// State is tracked explicitly (activeElements) and cleared at the START of every
// mouseover, rather than relying on a matching mouseout for the previous element. Some
// places (the Village map, for one) periodically redraw their whole ascii content on a
// timer, which can silently remove the element the mouse is still resting over -- a
// removed element never gets a mouseout, so a mouseout-driven "turn it back off" would
// get stuck on. Clearing at the start of mouseover makes this self-healing: whatever the
// next real pointer movement lands on (a button or empty space) resolves the state
// correctly, no matter what happened to the previous element in between.
class AsciiGroupHover {
    private static initialized: boolean = false;
    private static activeElements: HTMLElement[] = [];

    public static init(): void {
        if (AsciiGroupHover.initialized) return;
        AsciiGroupHover.initialized = true;

        document.addEventListener("mouseover", AsciiGroupHover.onMouseOver, true);
        // Safety net only, for the mouse leaving the browser window entirely (so no
        // further mouseover ever arrives to clean up after it).
        document.addEventListener("mouseout", AsciiGroupHover.onWindowMouseOut, true);
    }

    // Private methods
    private static onMouseOver(event: MouseEvent): void {
        var el: HTMLElement = AsciiGroupHover.findAsciiButton(<HTMLElement>event.target);

        AsciiGroupHover.deactivateCurrent();
        if (el !== null) AsciiGroupHover.activate(el);
    }

    private static onWindowMouseOut(event: MouseEvent): void {
        if (event.relatedTarget === null) AsciiGroupHover.deactivateCurrent();
    }

    // Walks up a few levels from the event target looking for the .asciiButton element
    // itself (in practice it always IS the target, since these spans have no children,
    // but we walk up defensively in case that ever changes).
    private static findAsciiButton(element: HTMLElement): HTMLElement {
        var current: HTMLElement = element;
        var depth: number = 0;

        while (current !== null && depth < 5) {
            if (AsciiGroupHover.hasClass(current, "asciiButton")) return current;
            current = current.parentElement;
            depth++;
        }

        return null;
    }

    private static getGroupClass(element: HTMLElement): string {
        var classes: string[] = (element.className || "").split(/\s+/);

        for (var i = 0; i < classes.length; i++) {
            if (classes[i] !== "" && classes[i] !== "asciiButton" && classes[i] !== "asciiGroupHover")
                return classes[i];
        }

        return null;
    }

    private static activate(element: HTMLElement): void {
        var groupClass: string = AsciiGroupHover.getGroupClass(element);
        var affected: HTMLElement[] = [];

        // No shared class to group by: just this single element (same as the old behaviour)
        if (groupClass === null) {
            AsciiGroupHover.toggleClass(element, true);
            affected.push(element);
        }
        else {
            // Highlight every element sharing this same class
            var group: NodeList = document.getElementsByClassName(groupClass);
            for (var i = 0; i < group.length; i++) {
                var groupEl: HTMLElement = <HTMLElement>group[i];
                AsciiGroupHover.toggleClass(groupEl, true);
                affected.push(groupEl);
            }
        }

        AsciiGroupHover.activeElements = affected;

        if (typeof AsciiPoiMarker !== "undefined") AsciiPoiMarker.show(affected);
    }

    private static deactivateCurrent(): void {
        if (AsciiGroupHover.activeElements.length === 0) return;

        for (var i = 0; i < AsciiGroupHover.activeElements.length; i++) {
            AsciiGroupHover.toggleClass(AsciiGroupHover.activeElements[i], false);
        }

        AsciiGroupHover.activeElements = [];

        if (typeof AsciiPoiMarker !== "undefined") AsciiPoiMarker.hide();
    }

    private static hasClass(element: HTMLElement, className: string): boolean {
        return (" " + element.className + " ").indexOf(" " + className + " ") !== -1;
    }

    private static toggleClass(element: HTMLElement, active: boolean): void {
        var has: boolean = AsciiGroupHover.hasClass(element, "asciiGroupHover");

        if (active && !has)
            element.className += " asciiGroupHover";
        else if (!active && has)
            element.className = element.className.replace(/\s*asciiGroupHover\b/, "");
    }
}
