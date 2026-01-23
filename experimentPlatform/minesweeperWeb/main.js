import {gameInit, renderGame} from "/modules/game.js"
import {preloadURL} from "/modules/helpRender.js"
import {leaderboard_refresh} from "/modules/leaderboard.js"
import {get_seed} from "/modules/apiWrapper.js"

// NOTE: this is just one-off code to pre-generate seeds for a selection of 3bv scores
// import {calculate3BV} from "/modules/game.js"
// // let threebvGoals = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40]
// let threebvGoals = [2, 5, 7, 8, 9, 10, 10, 11, 12, 13, 14, 15, 15, 16, 17, 17, 18, 19, 20, 22, 26, 30, 35, 40]
// let sources = []
// let threebv = 0;
// let seedy = undefined;
// 
// while (threebvGoals.length > 0) {
//     // seed = Math.floor(Date.now()/1000);
//     seedy = Date.now();
//     const field = gameInit(9, 9, 10, seedy);
//     threebv = calculate3BV(field);
//     console.log("found threebv", threebv, "for seed", seedy)
// 
//     if (! threebvGoals.includes(threebv)) continue;
//     threebvGoals = threebvGoals.filter(x => x != threebv)
//     console.log("accepted threebv", threebv, "for seed", seedy, "goals now", threebvGoals)
//     sources.push([seedy, threebv])
// }
// console.log("sources:", JSON.stringify(sources))

// const gameCanv = document.getElementById("firstCanvas");
// gameCanv.insertAdjacentElement("afterend", gameCanv2);

function sleep(milliseconds) {
	return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

/* generates the inital board
 * renders the initial board
 * generates hints, and passes to interaction listeners somehow
 * registers interaction listeners -> interaction listeners do some telemetry
*/

// NOTE: we're only running the experiment with 9x9 fields, but we'll leave groundwork for other fields so I can make this a fully fleshed out web game outwith the dissertation.

/* on each render, we first draw the base board
 * then we draw the mines remaining, restart button, timer
 * and lastly the grid.
 *
 * grid drawing is either: 0. a closed cell, 1. a closed flagged cell, 2. a numbered open cell with hint 0-9 (0 renders no number), 3. a mine (or explosion)
*/

// start loading necessary assets asynchronously
let assetPromises = []
assetPromises.push(preloadURL("./assets/background.png", "background"));
assetPromises.push(preloadURL("./assets/closedCell.png", "closedCell")); // field ID 0
assetPromises.push(preloadURL("./assets/flaggedCell.png", "flaggedCell")); // field ID 1
assetPromises.push(preloadURL("./assets/hint0Cell.png", "hint0Cell")); // field ID 2
assetPromises.push(preloadURL("./assets/hint1Cell.png", "hint1Cell")); // field ID 2
assetPromises.push(preloadURL("./assets/hint2Cell.png", "hint2Cell")); // field ID 2
assetPromises.push(preloadURL("./assets/hint3Cell.png", "hint3Cell")); // field ID 2
assetPromises.push(preloadURL("./assets/hint4Cell.png", "hint4Cell")); // field ID 2
assetPromises.push(preloadURL("./assets/hint5Cell.png", "hint5Cell")); // field ID 2
assetPromises.push(preloadURL("./assets/hint6Cell.png", "hint6Cell")); // field ID 2
assetPromises.push(preloadURL("./assets/hint7Cell.png", "hint7Cell")); // field ID 2
assetPromises.push(preloadURL("./assets/hint8Cell.png", "hint8Cell")); // field ID 2
assetPromises.push(preloadURL("./assets/mineCell.png", "mineCell")); // field ID 3
assetPromises.push(preloadURL("./assets/edgeSegmentOn.png", "edgeSegmentOn"));
assetPromises.push(preloadURL("./assets/edgeSegmentOff.png", "edgeSegmentOff"));
assetPromises.push(preloadURL("./assets/centerSegmentOn.png", "centerSegmentOn"));
assetPromises.push(preloadURL("./assets/centerSegmentOff.png", "centerSegmentOff"));
assetPromises.push(preloadURL("/assets/smileIdle.png", "smileIdle"));
assetPromises.push(preloadURL("/assets/smileBlink.png", "smileBlink"));
assetPromises.push(preloadURL("/assets/sadIdle.png", "sadIdle"));
assetPromises.push(preloadURL("/assets/sadBlink.png", "sadBlink"));

// pull leaderboard
leaderboard_refresh();

// check for a specified seed and load if present, otherwise get a seed from the server
const urlParams = new URLSearchParams(window.location.search);
let seed = parseInt(urlParams.get("seed"))
if (isNaN(seed)) {
    seed = await get_seed();
    seed = parseInt(seed); // HACK: get_seed sometimes returns "random" indicating we should use a random seed. parseInt for a string yields NaN, which gets caught by the isNaN check below.
}
console.log("seed:", seed);

// check for an existing user ID or create one on the assumption it's a new user
if (!localStorage.hasOwnProperty("userIDpriv")) localStorage.userIDpriv = Date.now() * 10 * Math.random(); // assumes we'll never have more than 10 people "signing up" per milisecond. if this somehow causes problems then I quit (maybe I should charge for sign ups?)
if (!localStorage.hasOwnProperty("userIDpub")) localStorage.userIDpub = Math.round(localStorage.userIDpriv).toString().slice(0, 5);

// populate the form with user IDs for whenever the user wants to submit a comment
document.getElementById("userIDprivInp").value = localStorage.userIDpriv;
document.getElementById("userIDpubInp").value = localStorage.userIDpub;

// setup fresh game
let gameInstance = gameInit(9, 9, 10, isNaN(seed) ? undefined : seed);

// check and wait for unfinised assets
for (const promise of assetPromises) await promise;

// insert the canvas where we need it
document.getElementById("content").prepend(gameInstance.ctx.canvas)

// render the first state of the game.
renderGame(gameInstance);
// note - subsequent states are triggered by user actions, so there is no game loop. there is however a regular render loop every second that is independent of actions.
