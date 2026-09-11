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
//
// Volume and mute are a device-level preference (like the browser's own volume), not part of
// a save slot -- they're kept in localStorage directly under fixed keys, completely separate
// from Saving/LocalSaving, so switching or loading a save slot never changes them.
class MusicBridge {
    // Place class name -> track path. Anything not listed here falls back to the fight theme
    // (if the place is a Quest, i.e. a combat/exploration screen) or the main theme otherwise.
    private static PLACE_TRACKS: any = {
        "Village": "music/places/village.mp3",
        "Forge": "music/places/forge.mp3",
        "SorceressHut": "music/places/sorceressHut.mp3",
        // The Cauldron is the witch's own workspace (reached from her hut), so it shares her
        // theme rather than getting a separate track.
        "Cauldron": "music/places/sorceressHut.mp3",
        "Lighthouse": "music/places/lighthouse.mp3",
        "Desert": "music/places/desert.mp3",
        // The Pier itself and jumping into the water off it (TheSea) share one theme, since
        // they're really the same moment continuing.
        "Pier": "music/places/theSea.mp3",
        "TheSea": "music/places/theSea.mp3",
        "TheCave": "music/places/theCave.mp3",
        // These two are specific boss encounters (each is its own Quest subclass), so they get
        // their own theme instead of falling back to the generic fight track.
        "MonkeyWizardQuest": "music/places/monkeyWizardQuest.mp3",
        "OctopusKingQuest": "music/places/octopusKingQuest.mp3",
        // Inventory / Save / Settings (Cfg) are menu-like screens rather than "places" with their
        // own atmosphere, so they all share one calmer, out-of-the-action theme.
        "Inventory": "music/menus.mp3",
        "Save": "music/menus.mp3",
        "Cfg": "music/menus.mp3"
    };

    private static MAIN_THEME: string = "music/main-theme.mp3";
    private static CALM_THEME: string = "music/where-the-clock-stops.mp3";
    private static MEDITATIVE_THEME: string = "music/a-room-without-hours.mp3";
    private static FIGHT_THEME: string = "music/fight.mp3";

    private static GENERAL_TRACKS: any = [
        "music/main-theme.mp3",
        "music/where-the-clock-stops.mp3",
        "music/a-room-without-hours.mp3"
    ];

    private static currentPlaceName: string = null;
    private static currentIsQuest: boolean = false;

    private static VOLUME_STORAGE_KEY: string = "musicBridgeVolume"; // 0-100
    private static MUTED_STORAGE_KEY: string = "musicBridgeMuted"; // "1" or "0"

    // Two <audio> elements so we can crossfade: one is always "active" (audible, playing the
    // current track) while the other is either silent/paused or mid-fade.
    private static audioA: HTMLAudioElement = null;
    private static audioB: HTMLAudioElement = null;
    private static activeIsA: boolean = true;

    private static currentTrack: string = null;

    // sliderVolume is what the volume slider is set to (0-1), independent of mute -- muting
    // doesn't move the slider, it just silences playback until unmuted.
    private static sliderVolume: number = 0.45;
    private static muted: boolean = false;
    private static isDucked: boolean = false;
    private static fadeTimer: any = null;

    // Autoplay gating: until the user has interacted with the page once, we just remember what
    // *should* be playing and apply it as soon as that first interaction happens.
    private static started: boolean = false;
    private static pendingPlaceName: string = null;
    private static pendingIsQuest: boolean = false;
    private static hasPending: boolean = false;

    private static isGeneralTrack(track: string): boolean {
        if (!track) return false;
        for (var i = 0; i < MusicBridge.GENERAL_TRACKS.length; i++) {
            if (track.indexOf(MusicBridge.GENERAL_TRACKS[i]) !== -1) return true;
        }
        return false;
    }

    private static isCurrentAreaGeneral(): boolean {
        if (MusicBridge.currentIsQuest) return false;
        if (!MusicBridge.currentPlaceName) return true;
        var placeTrack: string = MusicBridge.PLACE_TRACKS[MusicBridge.currentPlaceName];
        return !placeTrack;
    }

    // Weighted random selection:
    // 50% Main theme (music/main-theme.mp3)
    // 40% Where the Clock Stops (music/where-the-clock-stops.mp3)
    // 10% A Room Without Hours (music/a-room-without-hours.mp3)
    private static pickGeneralTrack(): string {
        var r: number = Math.random();
        if (r < 0.50) {
            return MusicBridge.MAIN_THEME;
        } else if (r < 0.90) {
            return MusicBridge.CALM_THEME;
        } else {
            return MusicBridge.MEDITATIVE_THEME;
        }
    }

    public static init(): void {
        if (MusicBridge.audioA !== null) return; // Already initialized

        MusicBridge.loadPreferences();

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
        MusicBridge.currentPlaceName = placeName;
        MusicBridge.currentIsQuest = isQuest;

        var track: string = MusicBridge.PLACE_TRACKS[placeName];
        if (!track) {
            if (isQuest) {
                track = MusicBridge.FIGHT_THEME;
            } else {
                // If we are already playing one of the general themes, don't restart or crossfade!
                if (MusicBridge.isGeneralTrack(MusicBridge.currentTrack)) {
                    return;
                }
                track = MusicBridge.pickGeneralTrack();
            }
        }

        if (track === MusicBridge.currentTrack) return; // Already playing (or about to play) this track

        if (!MusicBridge.started) {
            // No user gesture yet -- remember what should play once one happens.
            MusicBridge.pendingPlaceName = placeName;
            MusicBridge.pendingIsQuest = isQuest;
            MusicBridge.hasPending = true;
            return;
        }

        MusicBridge.startTrack(track);
    }

    private static startTrack(track: string): void {
        MusicBridge.currentTrack = track;

        var incoming: HTMLAudioElement = MusicBridge.activeIsA ? MusicBridge.audioB : MusicBridge.audioA;
        var outgoing: HTMLAudioElement = MusicBridge.activeIsA ? MusicBridge.audioA : MusicBridge.audioB;
        MusicBridge.activeIsA = !MusicBridge.activeIsA;

        incoming.src = track;
        // Place and combat tracks loop; general ambient tracks don't loop so they can naturally rotate
        incoming.loop = !MusicBridge.isGeneralTrack(track);
        incoming.volume = 0;
        incoming.currentTime = 0;

        try {
            var p: any = incoming.play();
            if (p && p.catch) {
                p.catch(function (err: any): void { /* Ignore -- browser withholding autoplay */ });
            }
        } catch (e) { /* Ignore */ }

        MusicBridge.crossfade(incoming, outgoing);
    }

    // 0-100, as driven by the header volume slider.
    public static setVolume(volumePercent: number): void {
        MusicBridge.sliderVolume = Math.max(0, Math.min(100, volumePercent)) / 100;
        MusicBridge.savePreferences();

        // Setting the slider above 0 while muted implicitly unmutes, same as most volume UIs.
        if (MusicBridge.muted && MusicBridge.sliderVolume > 0) MusicBridge.muted = false;

        MusicBridge.applyVolumeToActiveTrack();
    }

    public static getVolume(): number {
        return Math.round(MusicBridge.sliderVolume * 100);
    }

    public static toggleMute(): void {
        MusicBridge.muted = !MusicBridge.muted;
        MusicBridge.savePreferences();
        MusicBridge.applyVolumeToActiveTrack();
    }

    public static isMuted(): boolean {
        return MusicBridge.muted;
    }

    // Only meaningful once init() has run.
    public static isReady(): boolean {
        return MusicBridge.audioA !== null;
    }

    public static setDucked(ducked: boolean): void {
        MusicBridge.isDucked = ducked;
        MusicBridge.applyVolumeToActiveTrack();
    }

    private static effectiveVolume(): number {
        var vol: number = MusicBridge.muted ? 0 : MusicBridge.sliderVolume;
        if (MusicBridge.isDucked) vol *= 0.35;
        return vol;
    }

    // Applies the current effective volume to whichever track is actually audible right now,
    // without restarting a crossfade -- used when the user drags the slider or hits mute
    // outside of a place change.
    private static applyVolumeToActiveTrack(): void {
        if (MusicBridge.fadeTimer !== null) return; // A crossfade is already driving the volume; let it finish
        // activeIsA flips at the END of setPlace() to record which element is now playing,
        // so the currently-playing track is the OPPOSITE of what activeIsA points to here.
        var active: HTMLAudioElement = MusicBridge.activeIsA ? MusicBridge.audioA : MusicBridge.audioB;
        if (active) active.volume = MusicBridge.effectiveVolume();
    }

    private static loadPreferences(): void {
        try {
            var storedVolume: string = localStorage.getItem(MusicBridge.VOLUME_STORAGE_KEY);
            if (storedVolume !== null) {
                var parsed: number = parseInt(storedVolume, 10);
                if (!isNaN(parsed)) MusicBridge.sliderVolume = Math.max(0, Math.min(100, parsed)) / 100;
            }
            MusicBridge.muted = localStorage.getItem(MusicBridge.MUTED_STORAGE_KEY) === "1";
        } catch (e) { /* localStorage unavailable (e.g. private browsing) -- fall back to defaults */ }
    }

    private static savePreferences(): void {
        try {
            localStorage.setItem(MusicBridge.VOLUME_STORAGE_KEY, Math.round(MusicBridge.sliderVolume * 100).toString());
            localStorage.setItem(MusicBridge.MUTED_STORAGE_KEY, MusicBridge.muted ? "1" : "0");
        } catch (e) { /* Ignore -- preference just won't persist this session */ }
    }

    private static createAudioElement(): HTMLAudioElement {
        var el: HTMLAudioElement = <HTMLAudioElement>document.createElement("audio");
        el.loop = true;
        el.volume = 0;
        el.addEventListener("ended", function (): void {
            MusicBridge.handleTrackEnded(el);
        });
        document.body.appendChild(el);
        return el;
    }

    private static handleTrackEnded(el: HTMLAudioElement): void {
        var active: HTMLAudioElement = MusicBridge.activeIsA ? MusicBridge.audioA : MusicBridge.audioB;
        if (el !== active) return;
        if (!MusicBridge.isCurrentAreaGeneral()) return;

        var nextTrack: string = MusicBridge.pickGeneralTrack();
        MusicBridge.startTrack(nextTrack);
    }

    private static crossfade(incoming: HTMLAudioElement, outgoing: HTMLAudioElement): void {
        if (MusicBridge.fadeTimer !== null) clearInterval(MusicBridge.fadeTimer);

        var totalSteps: number = 30; // ~1.2s fade at 40ms/step
        var step: number = 0;
        var target: number = MusicBridge.effectiveVolume();
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

// Tiny header widget wiring for MusicBridge: keeps the volume slider and the
// mute button's visual state (icon + ".music-muted" class) in sync with
// MusicBridge's actual state, both on load and after every user interaction
// with the control. Kept separate from MusicBridge itself so MusicBridge stays
// a pure audio engine with no DOM/UI concerns of its own.
class MusicVolumeUI {
    public static init(): void {
        if (typeof MusicBridge === "undefined" || !MusicBridge.isReady()) return;

        var slider: any = document.getElementById("music-volume-slider");
        if (slider) slider.value = MusicBridge.getVolume().toString();

        MusicVolumeUI.refresh();
    }

    public static refresh(): void {
        if (typeof MusicBridge === "undefined") return;

        var container: HTMLElement = document.getElementById("music-control");
        var muteBtn: HTMLElement = document.getElementById("music-mute-btn");
        var slider: any = document.getElementById("music-volume-slider");

        var muted: boolean = MusicBridge.isMuted();

        if (container) {
            if (muted) container.className = (container.className + " music-muted").trim();
            else container.className = container.className.replace(/\s*music-muted\s*/g, " ").trim();
        }

        if (muteBtn) muteBtn.innerHTML = muted ? "&#9835;" : "&#9834;"; // filled vs. outline note glyph; color flips via .music-muted
        if (slider) slider.value = MusicBridge.getVolume().toString();
    }
}
