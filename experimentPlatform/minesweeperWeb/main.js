import {gameInit, renderGame, interactHandler} from "/modules/game.js"
import {preloadURL} from "/modules/helpRender.js"
import {leaderboard_refresh} from "/modules/leaderboard.js"

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

/* on each render, we first draw the base board
 * then we draw the mines remaining, restart button, timer
 * and lastly the grid.
 *
 * grid drawing is either: 0. a closed cell, 1. a closed flagged cell, 2. a numbered open cell with hint 0-9 (0 renders no number), 3. a mine (or explosion)
*/

leaderboard_refresh();

let gameInstance = gameInit(gameCtx, 9, 9, 10);

// prepare necessary assets
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
for (const promise of assetPromises) await promise;

// render the first state of the game.
renderGame(gameInstance);
// note - subsequent states are triggered by user actions, so there is no game loop. there is however a regular render loop every second that is independent of actions.

// TODO: register user action listeners
// HACK: interactHandler triggers a re-render, and timer rendering requires the timer handler be set up,
// so the timer handler needs to be registered before the interact for the necessary data to exist on the first execution of the ineract handler.

// gameCanv.addEventListener("mousedown", (e) => { return timerHandler(e, gameInstance) }, {once : true});
gameCanv.addEventListener("mousedown", (e) => { return interactHandler(e, gameInstance) });
gameCanv.addEventListener("mouseup"  , (e) => { return interactHandler(e, gameInstance) });
// gameCanv.addEventListener('touchstart', interactHandler); // relic from touch support.. apprently touches issue both touchend and mouseup? doesnt make sense, but convientient.
