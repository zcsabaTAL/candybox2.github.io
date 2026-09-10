///<reference path="Quest.ts"/>

// Background music for the "hybrid UI" overlay -- a main theme that plays everywhere by
// default, a generic "fight" track for any quest/combat screen that doesn't have its own
// score, and a handful of place-specific tracks (Village, the witch's hut, the lighthouse's
// cyclops, the desert) that take over while you're on that particular screen. Crossfades
// between tracks instead of hard-cutting, and never touches game logic -- it only watches
// <body data-place="..."> (set by UIBridge.updateHeaders()) the same way the rest of the
// overlay does.
//
// Browsers block audio autoplay before the user has interacted with the page at all, so
// playback only actually starts after the first click/keydown anywhere on the page -- which
// happens naturally the moment someone clicks any of the game's own buttons. Until then, the
// desired track is just remembered and applied once that first interaction happens.
class MusicBridge {
    // Place class name -> track path. Anything not listed here falls back to the fight theme
    // (if the place is a Quest, i.e. a combat/exploration screen) or the main theme otherwise.
    private static PLACE_TRACKS: any = {
        "Village": "music/places/village.mp3",
        "SorceressHut": "music/places/sorceressHut.mp3",
        "Lighthouse": "music/places/lighthouse.mp3",
        "Desert": "music/places/desert.mp3"
    };

    private static MAIN_THEME: string = "music/main-theme.mp3";
    private static FIGHT_THEME: string = "music/fight.mp3";

    // Two <audio> elements so we can crossfade: one is always "active" (audible, playing the
    // current track) while the other is either silent/paused or mid-fade.
    private static audioA: HTMLAudioElement = null;
    private static audioB: HTMLAudioElement = null;
    private static activeIsA: boolean = true;

    private static currentTrack: string = null;
    private static desiredVolume: number = 0.45;
    private static fadeTimer: any = null;

    // Autoplay gating: until the user has interacted with the page once, we just remember what
    // *should* be playing and apply it as soon as that first interaction happens.
    private static started: boolean = false;
    private static pendingPlaceName: string = null;
    private static pendingIsQuest: boolean = false;
    private static hasPending: boolean = false;

    public static init(): void {
        if (MusicBridge.audioA !== null) return; // Already initialized

        MusicBridge.audioA = MusicBridge.createAudioElement();
        MusicBridge.audioB = MusicBridge.createAudioElement();

        var startOnFirstInteraction = function (): void {
            document.removeEventListener("click", startOnFirstInteraction);
            document.removeEventListener("keydown", startOnFirstInteraction);
            MusicBridge.started = true;
            if (MusicBridge.hasPending) {
                MusicBridge.hasPending = false;
                MusicBridge.setPlace(MusicBridge.pendingPlaceName, MusicBridge.pendingIsQuest);
            }
        };
        document.addEventListener("click", startOnFirstInteraction);
        document.addEventListener("keydown", startOnFirstInteraction);
    }

    // Called every time UIBridge notices the current place changed. isQuest tells us whether
    // to fall back to the fight theme (true) or the main theme (false) when there's no
    // place-specific track.
    public static setPlace(placeName: string, isQuest: boolean): void {
        var track: string = MusicBridge.PLACE_TRACKS[placeName];
        if (!track) track = isQuest ? MusicBridge.FIGHT_THEME : MusicBridge.MAIN_THEME;

        if (track === MusicBridge.currentTrack) return; // Already playing (or about to play) this track

        if (!MusicBridge.started) {
            // No user gesture yet -- remember what should play once one happens.
            MusicBridge.pendingPlaceName = placeName;
            MusicBridge.pendingIsQuest = isQuest;
            MusicBridge.hasPending = true;
            return;
        }

        MusicBridge.currentTrack = track;

        var incoming: HTMLAudioElement = MusicBridge.activeIsA ? MusicBridge.audioB : MusicBridge.audioA;
        var outgoing: HTMLAudioElement = MusicBridge.activeIsA ? MusicBridge.audioA : MusicBridge.audioB;
        MusicBridge.activeIsA = !MusicBridge.activeIsA;

        incoming.src = track;
        incoming.volume = 0;
        incoming.currentTime = 0;
        try { incoming.play(); } catch (e) { /* Ignore -- e.g. browser still withholding autoplay */ }

        MusicBridge.crossfade(incoming, outgoing);
    }

    // Public setter so a future volume/mute control can hook in without touching the rest of
    // this class.
    public static setVolume(volume: number): void {
        MusicBridge.desiredVolume = volume;
        var active: HTMLAudioElement = MusicBridge.activeIsA ? MusicBridge.audioB : MusicBridge.audioA;
        if (MusicBridge.fadeTimer === null) active.volume = volume;
    }

    private static createAudioElement(): HTMLAudioElement {
        var el: HTMLAudioElement = <HTMLAudioElement>document.createElement("audio");
        el.loop = true;
        el.volume = 0;
        document.body.appendChild(el);
        return el;
    }

    private static crossfade(incoming: HTMLAudioElement, outgoing: HTMLAudioElement): void {
        if (MusicBridge.fadeTimer !== null) clearInterval(MusicBridge.fadeTimer);

        var totalSteps: number = 30; // ~1.2s fade at 40ms/step
        var step: number = 0;
        var target: number = MusicBridge.desiredVolume;
        var wasPlaying: boolean = !outgoing.paused;

        MusicBridge.fadeTimer = setInterval(function (): void {
            step += 1;
            var t: number = step / totalSteps;
            incoming.volume = Math.min(target, target * t);
            if (wasPlaying) outgoing.volume = Math.max(0, target * (1 - t));

            if (step >= totalSteps) {
                clearInterval(MusicBridge.fadeTimer);
                MusicBridge.fadeTimer = null;
                outgoing.pause();
            }
        }, 40);
    }
}
