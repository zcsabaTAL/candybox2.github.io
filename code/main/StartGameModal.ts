///<reference path="LocalSaving.ts"/>
///<reference path="main.ts"/>

class StartGameModal {
    private static overlayElement: HTMLElement = null;

    public static init(): void {
        // Find existing saves across slots 1..5
        var saves: any[] = [];
        var lastUsedSlotId: string = "slot1";

        if (LocalSaving.supportsLocalSaving()) {
            var storedLastSlot = localStorage.getItem("lastUsedSlotId");
            if (storedLastSlot != null && storedLastSlot !== "") {
                lastUsedSlotId = storedLastSlot;
            }

            for (var i = 1; i <= 5; i++) {
                var sId: string = "slot" + i;
                var dateStr: string = LocalSaving.loadString(sId);
                if (dateStr != null && dateStr !== "") {
                    var candiesStr: string = LocalSaving.loadString(sId + ".gameCandiesCurrent");
                    var lolliesStr: string = LocalSaving.loadString(sId + ".gameLollipopsCurrent");
                    saves.push({
                        id: sId,
                        number: i,
                        date: dateStr,
                        candies: candiesStr != null ? candiesStr : "0",
                        lollipops: lolliesStr != null ? lolliesStr : "0"
                    });
                }
            }
        }

        // Identify default slot to resume: prefer lastUsedSlotId if it has data, else first available save
        var defaultSave: any = null;
        for (var j = 0; j < saves.length; j++) {
            if (saves[j].id === lastUsedSlotId) {
                defaultSave = saves[j];
                break;
            }
        }
        if (defaultSave == null && saves.length > 0) {
            defaultSave = saves[0];
        }

        StartGameModal.render(saves, defaultSave);
    }

    private static formatNumber(val: string): string {
        var num: number = parseInt(val, 10);
        if (isNaN(num)) return val;
        // Format with commas / spaces
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
    }

    private static render(saves: any[], defaultSave: any): void {
        // Remove old overlay if present
        var existing = document.getElementById("start-game-modal-overlay");
        if (existing != null && existing.parentNode != null) {
            existing.parentNode.removeChild(existing);
        }

        var overlay = document.createElement("div");
        overlay.id = "start-game-modal-overlay";
        StartGameModal.overlayElement = overlay;

        var html: string = "";
        html += '<div class="start-game-modal-card">';
        html += '  <div class="start-game-modal-glow"></div>';
        html += '  <div class="start-game-brand">';
        html += '    <div class="start-game-badge">CANDY BOX 2</div>';
        html += '    <h1 class="start-game-title">ÜDVÖZLÜNK AZ ÉDESSÉGEK BIRODALMÁBAN</h1>';
        html += '    <p class="start-game-subtitle">Hogyan szeretnéd folytatni a kalandot?</p>';
        html += '  </div>';

        if (defaultSave != null) {
            var formattedCandies: string = StartGameModal.formatNumber(defaultSave.candies);
            var formattedLollies: string = StartGameModal.formatNumber(defaultSave.lollipops);

            html += '  <div class="start-game-save-panel">';
            html += '    <div class="start-game-save-icon">&#9876;</div>';
            html += '    <div class="start-game-save-info">';
            html += '      <div class="start-game-save-header">';
            html += '        <span class="start-game-save-title">Legutóbbi mentés: <strong>Slot ' + defaultSave.number + '</strong></span>';
            html += '        <span class="start-game-save-date">' + defaultSave.date + '</span>';
            html += '      </div>';
            html += '      <div class="start-game-save-stats">';
            html += '        <span class="stat-pill candy-pill">&#9670; ' + formattedCandies + ' cukor</span>';
            if (defaultSave.lollipops !== "0") {
                html += '        <span class="stat-pill lolly-pill">&#9899; ' + formattedLollies + ' nyalóka</span>';
            }
            html += '      </div>';
            html += '    </div>';
            html += '  </div>';

            // Action buttons
            html += '  <div class="start-game-actions">';
            html += '    <button class="start-game-btn start-game-btn-continue" id="sg-btn-continue">';
            html += '      <span class="sg-btn-glow"></span>';
            html += '      <span class="sg-btn-icon">&#9658;</span>';
            html += '      <span class="sg-btn-content">';
            html += '        <span class="sg-btn-main">MENTÉS FOLYTATÁSA</span>';
            html += '        <span class="sg-btn-sub">Slot ' + defaultSave.number + ' betöltése és játék</span>';
            html += '      </span>';
            html += '    </button>';

            html += '    <button class="start-game-btn start-game-btn-new" id="sg-btn-new">';
            html += '      <span class="sg-btn-icon">&#10022;</span>';
            html += '      <span class="sg-btn-content">';
            html += '        <span class="sg-btn-main">ÚJ JÁTÉK KEZDÉSE</span>';
            html += '        <span class="sg-btn-sub">Tiszta lappal indulás a doboznál</span>';
            html += '      </span>';
            html += '    </button>';
            html += '  </div>';

            // If there are multiple saves, offer slot selector
            if (saves.length > 1) {
                html += '  <div class="start-game-other-slots-container">';
                html += '    <div class="start-game-other-slots-title">VAGY VÁLASSZ MÁSIK MENTÉST:</div>';
                html += '    <div class="start-game-slots-list">';
                for (var k = 0; k < saves.length; k++) {
                    var s = saves[k];
                    var isSelected = (s.id === defaultSave.id);
                    var selectedClass = isSelected ? " selected" : "";
                    html += '      <button class="start-game-slot-chip' + selectedClass + '" data-slot="' + s.id + '">';
                    html += '        Slot ' + s.number + ' (' + StartGameModal.formatNumber(s.candies) + ' cukor)';
                    html += '      </button>';
                }
                html += '    </div>';
                html += '  </div>';
            }
        } else {
            // No saves found
            html += '  <div class="start-game-empty-panel">';
            html += '    <div class="start-game-empty-icon">&#10024;</div>';
            html += '    <div class="start-game-empty-text">Még nincs mentett játékállásod ezen a készüléken.</div>';
            html += '  </div>';

            html += '  <div class="start-game-actions single-action">';
            html += '    <button class="start-game-btn start-game-btn-continue" id="sg-btn-new">';
            html += '      <span class="sg-btn-glow"></span>';
            html += '      <span class="sg-btn-icon">&#9658;</span>';
            html += '      <span class="sg-btn-content">';
            html += '        <span class="sg-btn-main">ÚJ JÁTÉK KEZDÉSE</span>';
            html += '        <span class="sg-btn-sub">Kaland megkezdése a dobozzal</span>';
            html += '      </span>';
            html += '    </button>';
            html += '  </div>';
        }

        html += '</div>'; // .start-game-modal-card

        overlay.innerHTML = html;
        document.body.appendChild(overlay);

        // Attach event handlers
        var selectedSlotId: string = defaultSave != null ? defaultSave.id : "slot1";

        // Slot chips click
        var chips = overlay.getElementsByClassName("start-game-slot-chip");
        for (var c = 0; c < chips.length; c++) {
            (function(chipEl: HTMLElement) {
                chipEl.onclick = function() {
                    selectedSlotId = chipEl.getAttribute("data-slot");
                    // Update active chip style
                    for (var x = 0; x < chips.length; x++) {
                        var chipItem: HTMLElement = <HTMLElement>chips[x];
                        chipItem.className = chipItem.className.replace(" selected", "");
                    }
                    chipEl.className += " selected";

                    // Update continue button subtext
                    var contSub = overlay.querySelector("#sg-btn-continue .sg-btn-sub");
                    if (contSub != null) {
                        contSub.textContent = selectedSlotId.toUpperCase() + " betöltése és játék";
                    }
                };
            })(<HTMLElement>chips[c]);
        }

        // Continue button click
        var contBtn = document.getElementById("sg-btn-continue");
        if (contBtn != null) {
            contBtn.onclick = function() {
                StartGameModal.dismiss(function() {
                    Main.bootGame(MainLoadingType.LOCAL, selectedSlotId);
                });
            };
        }

        // New Game button click
        var newBtn = document.getElementById("sg-btn-new");
        if (newBtn != null) {
            newBtn.onclick = function() {
                StartGameModal.dismiss(function() {
                    Main.bootGame(MainLoadingType.NONE, null);
                });
            };
        }
    }

    private static dismiss(callback: () => void): void {
        if (StartGameModal.overlayElement != null) {
            StartGameModal.overlayElement.className = "closing";
            setTimeout(function() {
                if (StartGameModal.overlayElement != null && StartGameModal.overlayElement.parentNode != null) {
                    StartGameModal.overlayElement.parentNode.removeChild(StartGameModal.overlayElement);
                    StartGameModal.overlayElement = null;
                }
                if (callback) callback();
            }, 300);
        } else {
            if (callback) callback();
        }
    }
}
