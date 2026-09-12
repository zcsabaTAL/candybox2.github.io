"use strict";

// These fixtures are declarative overrides on top of the registered Candy Box 2
// defaults. The browser helper materializes the complete legacy slot through
// LocalSaving.save(), so every currently registered key is present.
module.exports = {
    earlyGame: {
        slotId: "slot1",
        bools: {
            statusBarUnlocked: true,
            statusBarUnlockedSave: true
        },
        numbers: {
            gameCandiesAccumulated: 30,
            gameCandiesCurrent: 30,
            gameCandiesMax: 30
        },
        strings: {}
    },

    forgeWoodenSwordBefore: {
        slotId: "slot1",
        bools: {
            statusBarUnlocked: true,
            statusBarUnlockedMap: true,
            statusBarUnlockedSave: true,
            gridItemPossessedMainMap: true,
            forgeBoughtWoodenSword: false,
            eqItemWeaponWoodenSword: false
        },
        numbers: {
            gameCandiesAccumulated: 4000,
            gameCandiesCurrent: 4000,
            gameCandiesMax: 4000
        },
        strings: {}
    },

    forgeWoodenSwordAfter: {
        slotId: "slot1",
        bools: {
            statusBarUnlocked: true,
            statusBarUnlockedMap: true,
            statusBarUnlockedSave: true,
            statusBarUnlockedInventory: true,
            gridItemPossessedMainMap: true,
            forgeBoughtWoodenSword: true,
            eqItemWeaponWoodenSword: true
        },
        numbers: {
            gameCandiesAccumulated: 4000,
            gameCandiesCurrent: 3850,
            gameCandiesMax: 4000
        },
        strings: {}
    }
};
