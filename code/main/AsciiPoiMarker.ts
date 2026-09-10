// A small floating glow-dot that hovers over whichever multi-row ASCII object (a house
// on the Village map, a landmark on the World Map, etc.) currently has AsciiGroupHover's
// group-highlight active -- a lightweight visual companion to that highlight, in the
// spirit of the glowing waypoint markers on the reference mockups. Purely decorative: it
// adds no text of its own (the game's existing tooltip/name system, wherever a place has
// one, still does that job) and it only activates on the places that got the reskin
// treatment (see REVISKINNED_PLACES below) -- see <body data-place="..."> set by
// UIBridge. Its color comes entirely from CSS (.ascii-poi-marker, place-scoped), so this
// class doesn't need to know or care which place it's showing on.
class AsciiPoiMarker {
    private static markerEl: HTMLElement = null;
    // Places that have gotten the visual reskin treatment and should show the marker.
    private static REVISKINNED_PLACES: string[] = ["Village", "MainMap"];

    public static show(elements: HTMLElement[]): void {
        var place: string = document.body.getAttribute("data-place");
        if (AsciiPoiMarker.REVISKINNED_PLACES.indexOf(place) === -1) return;

        var box = AsciiPoiMarker.boundingBoxOf(elements);
        if (box === null) return;

        var marker: HTMLElement = AsciiPoiMarker.ensureMarker();
        marker.style.left = (box.left + box.width / 2) + "px";
        marker.style.top = (box.top + box.height / 2) + "px";
        marker.className = "ascii-poi-marker ascii-poi-marker-active";
    }

    public static hide(): void {
        if (AsciiPoiMarker.markerEl !== null)
            AsciiPoiMarker.markerEl.className = "ascii-poi-marker";
    }

    // Private methods
    private static ensureMarker(): HTMLElement {
        if (AsciiPoiMarker.markerEl === null) {
            var el: HTMLElement = document.createElement("div");
            el.className = "ascii-poi-marker";
            document.body.appendChild(el);
            AsciiPoiMarker.markerEl = el;
        }

        return AsciiPoiMarker.markerEl;
    }

    private static boundingBoxOf(elements: HTMLElement[]): any {
        if (elements.length === 0) return null;

        var left: number = Infinity, top: number = Infinity, right: number = -Infinity, bottom: number = -Infinity;

        for (var i = 0; i < elements.length; i++) {
            var r: ClientRect = elements[i].getBoundingClientRect();
            if (r.left < left) left = r.left;
            if (r.top < top) top = r.top;
            if (r.right > right) right = r.right;
            if (r.bottom > bottom) bottom = r.bottom;
        }

        return { left: left, top: top, width: right - left, height: bottom - top };
    }
}
