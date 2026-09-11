class VoiceBridge {
    private static currentAudio: HTMLAudioElement = null;
    private static dialogueTimer: number = null;
    private static currentPlace: string = null;
    private static volume: number = 0.95;

    public static playLighthouseQuestion(questionId: string): void {
        var playerFile: string = "audio/voice/player/" + questionId + ".mp3";
        var cyclopsFile: string = "audio/voice/cyclops/" + questionId + "Speech.mp3";
        VoiceBridge.playDialogue(playerFile, cyclopsFile);
    }

    public static playLighthouseEvent(eventId: string): void {
        var cyclopsFile: string = "audio/voice/cyclops/" + eventId + ".mp3";
        VoiceBridge.playSingle(cyclopsFile);
    }

    public static playDragonEvent(eventId: string): void {
        var dragonFile: string = "audio/voice/dragon/" + eventId + ".wav";
        VoiceBridge.playSingle(dragonFile);
    }

    public static playDialogue(playerTrack: string, responderTrack: string): void {
        VoiceBridge.stop();

        if (typeof MusicBridge !== "undefined") {
            MusicBridge.setDucked(true);
        }

        try {
            var audio: HTMLAudioElement = new Audio(playerTrack);
            audio.volume = VoiceBridge.volume;
            VoiceBridge.currentAudio = audio;

            audio.addEventListener("ended", function (): void {
                VoiceBridge.currentAudio = null;
                // Natural conversational pause between question and answer
                VoiceBridge.dialogueTimer = setTimeout(function (): void {
                    VoiceBridge.dialogueTimer = null;
                    VoiceBridge.playResponder(responderTrack);
                }, 350);
            });

            var p: any = audio.play();
            if (p && p.catch) {
                p.catch(function (err: any): void {
                    console.log("Player audio playback prevented or failed:", err);
                    if (typeof MusicBridge !== "undefined") {
                        MusicBridge.setDucked(false);
                    }
                });
            }
        } catch (e) {
            console.log("Voice error:", e);
            if (typeof MusicBridge !== "undefined") {
                MusicBridge.setDucked(false);
            }
        }
    }

    private static playResponder(responderTrack: string): void {
        try {
            var audio: HTMLAudioElement = new Audio(responderTrack);
            audio.volume = VoiceBridge.volume;
            VoiceBridge.currentAudio = audio;

            audio.addEventListener("ended", function (): void {
                VoiceBridge.currentAudio = null;
                if (typeof MusicBridge !== "undefined") {
                    MusicBridge.setDucked(false);
                }
            });

            var p: any = audio.play();
            if (p && p.catch) {
                p.catch(function (err: any): void {
                    console.log("Responder audio playback prevented or failed:", err);
                    if (typeof MusicBridge !== "undefined") {
                        MusicBridge.setDucked(false);
                    }
                });
            }
        } catch (e) {
            console.log("Responder voice error:", e);
            if (typeof MusicBridge !== "undefined") {
                MusicBridge.setDucked(false);
            }
        }
    }

    public static playSingle(trackPath: string): void {
        VoiceBridge.stop();

        if (typeof MusicBridge !== "undefined") {
            MusicBridge.setDucked(true);
        }

        try {
            var audio: HTMLAudioElement = new Audio(trackPath);
            audio.volume = VoiceBridge.volume;
            VoiceBridge.currentAudio = audio;

            audio.addEventListener("ended", function (): void {
                VoiceBridge.currentAudio = null;
                if (typeof MusicBridge !== "undefined") {
                    MusicBridge.setDucked(false);
                }
            });

            var p2: any = audio.play();
            if (p2 && p2.catch) {
                p2.catch(function (err: any): void {
                    console.log("Audio playback error:", err);
                    if (typeof MusicBridge !== "undefined") {
                        MusicBridge.setDucked(false);
                    }
                });
            }
        } catch (e) {
            console.log("Voice error:", e);
            if (typeof MusicBridge !== "undefined") {
                MusicBridge.setDucked(false);
            }
        }
    }

    public static stop(): void {
        if (VoiceBridge.dialogueTimer !== null) {
            clearTimeout(VoiceBridge.dialogueTimer);
            VoiceBridge.dialogueTimer = null;
        }

        if (VoiceBridge.currentAudio !== null) {
            try {
                VoiceBridge.currentAudio.pause();
                VoiceBridge.currentAudio.currentTime = 0;
            } catch (e) {}
            VoiceBridge.currentAudio = null;
        }

        if (typeof MusicBridge !== "undefined") {
            MusicBridge.setDucked(false);
        }
    }

    public static setPlace(placeName: string): void {
        if (VoiceBridge.currentPlace !== null && VoiceBridge.currentPlace !== placeName) {
            VoiceBridge.stop();
        }
        VoiceBridge.currentPlace = placeName;
    }
}
