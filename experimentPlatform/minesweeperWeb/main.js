import {mineGen, hintGen, renderGame} from "/modules/game.js"
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
let mineLayout = mineGen();
let mineHints = hintGen(mineLayout);


/* on each render, we first draw the base board
 * then we draw the mines remaining, restart button, timer
 * and lastly the grid.
 *
 * grid drawing is either: 0. a closed cell, 1. a closed flagged cell, 2. a numbered open cell with hint 0-9 (0 renders no number), 3. a mine (or explosion)
*/
// prepare the starting field. note: the field is a 9x9 grid.
let fieldState = Array(9).fill(Array(9).fill(0)); // filled with code 0 for closed cells.

// prepare necessary assets
await preloadURL("./assets/closedCell.png", "closedCell");
await preloadURL("./assets/background.png", "background");

// render the first state of the game.
renderGame(gameCtx, fieldState, mineHints, 0, 9, 9);
// note that subsequent game states happen as a result of user actions,
// hence the processing and subsequent rendering of future game states happens from there.

// TODO: register user action listeners
