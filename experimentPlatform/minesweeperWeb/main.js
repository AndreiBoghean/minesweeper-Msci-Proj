import {mineGen, hintGen, renderGame, interactHandler} from "/modules/game.js"
import {preloadURL} from "/modules/helpRender.js"

const gameCanv = document.getElementById("gameView");
const gameCtx = gameCanv.getContext("2d");

function sleep(milliseconds) {
	return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

/* generates the inital board
 * renders the initial board
 * generates hints, and passes to interaction listeners somehow
 * registers interaction listeners -> interaction listeners do some telemetry
*/

// NOTE: we're only running the experiment with 9x9 fields, but we'll leave groundwork for other fields so I can make this a fully fleshed out web game outwith the dissertation.

let fieldWidth = 9;
let fieldHeight = 9;
let [mineLayout, mineSeed] = mineGen(fieldWidth, fieldHeight);
let mineHints = hintGen(mineLayout);
let startTime = 0 // TODO: need to link this with start button

/* on each render, we first draw the base board
 * then we draw the mines remaining, restart button, timer
 * and lastly the grid.
 *
 * grid drawing is either: 0. a closed cell, 1. a closed flagged cell, 2. a numbered open cell with hint 0-9 (0 renders no number), 3. a mine (or explosion)
*/
// prepare the starting field.
let fieldState = []
for (let _ = 0; _ < fieldHeight ; _++) {
    fieldState.push(Array(fieldWidth).fill(0))
}

function printer2d(thing) { for (const row of thing) {console.log(row)}}
// console.log("intial field state:");
// printer2d(fieldState)
// console.log("given mine randomisation:");
// printer2d(mineLayout)
// console.log("computed mine hints:");
// printer2d(mineHints)

let gameInstance = { ctx: gameCtx, fieldState: fieldState, mineLayout: mineLayout, mineHints: mineHints, startTime: startTime, fieldWidth: fieldWidth, fieldHeight: fieldHeight }


// prepare necessary assets
await preloadURL("./assets/background.png", "background");
await preloadURL("./assets/closedCell.png", "closedCell"); // field ID 0
await preloadURL("./assets/flaggedCell.png", "flaggedCell"); // field ID 1
await preloadURL("./assets/hint0Cell.png", "hint0Cell"); // field ID 2
await preloadURL("./assets/hint1Cell.png", "hint1Cell"); // field ID 2
await preloadURL("./assets/hint2Cell.png", "hint2Cell"); // field ID 2
await preloadURL("./assets/hint3Cell.png", "hint3Cell"); // field ID 2
await preloadURL("./assets/hint4Cell.png", "hint4Cell"); // field ID 2
await preloadURL("./assets/hint5Cell.png", "hint5Cell"); // field ID 2
await preloadURL("./assets/hint6Cell.png", "hint6Cell"); // field ID 2
await preloadURL("./assets/hint7Cell.png", "hint7Cell"); // field ID 2
await preloadURL("./assets/hint8Cell.png", "hint8Cell"); // field ID 2
await preloadURL("./assets/mineCell.png", "mineCell"); // field ID 3

// render the first state of the game.
renderGame(gameInstance);
// note that subsequent game states happen as a result of user actions,
// hence the processing and subsequent rendering of future game states happens from there.


// TODO: register user action listeners
gameCanv.addEventListener('mousedown', (e) => { return interactHandler(e, gameInstance) });
// gameCanv.addEventListener('touchstart', interactHandler); // relic from touch support.. apprently touches issue both touchend and mouseup? doesnt make sense, but convientient.
