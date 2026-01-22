import {placePreloaded} from "/modules/helpRender.js"
import {submit_playthrough} from "/modules/apiWrapper.js"
import {leaderboard_refresh} from "/modules/leaderboard.js"
import {get_seed} from "/modules/apiWrapper.js"

export function calculate3BV(game) {
    // 3bv calculated as (all squares) minus (mine count)
    let threebv = game.fieldWidth*game.fieldHeight;
    let unclickables = [];
    for (let y=0 ; y < game.fieldWidth ; y++)
        for (let x=0 ; x < game.fieldWidth ; x++) {
            const i = (y+1)*game.fieldWidth+x;

            if (unclickables.includes(i))
                continue;

            else if (game.mineHints[y][x] == 0 && game.mineLayout[y][x] == 0) { // if cell is a non-mine with an empty hint
                // console.log("didnt skip", x, y)
                threebv += 1;
                // unclickables.push(i);

                const recuraboye = (eggs, wai) => {
                    const j = (wai+1)*game.fieldWidth+eggs;
                    if (unclickables.includes(j)) return;
                    if (game.mineLayout[wai][eggs] == 0) {
                        // console.log(unclickables, j, eggs, wai, game.mineHints[wai][eggs], game.mineLayout[wai][eggs])
                        // game.fieldState[wai][eggs] = 1;
                        unclickables.push(j); // if cell has an empty hint

                        if (game.mineHints[wai][eggs] == 0) neighbour_operation(game.fieldWidth, game.fieldHeight, eggs, wai, recuraboye);
                    }
                };
                recuraboye(x, y);
            }

            else if (game.mineLayout[y][x] == 1) // if cell is a mine
            // {game.fieldState[y][x] = 1;  unclickables.push((y+1)*game.fieldWidth+x); }
            { unclickables.push((y+1)*game.fieldWidth+x); }

            // else if ((game.mineLayout[y][x] != 1) && (game.mineHints[y][x] != 0)) // the cell isnt a mine and isnt a zero-hint
            //     neighbour_operation(game.fieldWidth, game.fieldHeight, x, y, (xAdj, yAdj) => { // for each of the cell's neighbours that isnt off the field..
            //         // if the neighbour cell isnt a mine, has a 0 hint, and isnt already accounted for... then count it.
            //         if ((game.mineLayout[yAdj][xAdj] != 1) && (game.mineHints[yAdj][xAdj] == 0) && (!unclickables.includes((yAdj+1)*game.fieldWidth+xAdj))) unclickables.push((yAdj+1)*game.fieldWidth+xAdj)
            //     });

            // else {
            //     console.error("cell index missed in 3bv calculation", x, y)
            //     game.fieldState[y][x] = 1;
            // }
        }

    // console.log("unclickables:", unclickables);
    threebv -= unclickables.length;
    //
    // console.log("thing1", (game.fieldWidth*game.fieldHeight));
    // console.log("thing1", (game.mineHints.reduce((r1, r2) => {return r1.concat(r2)})));
    // console.log("thing1", (game.mineCount));
    // let threebv = (game.fieldWidth*game.fieldHeight) - (game.mineHints.reduce((r1, r2) => {return r1.concat(r2)}).filter(c => c == 0).length) - (neighboursEmpty.length) - (game.mineCount);
    console.log("calculated 3bv", threebv)

    return threebv;
}

export function gameInit(fieldWidth, fieldHeight, mineCount, seed=undefined) {
     // prepare a canvas to keep our game instance
    const gameCanv = document.createElement("canvas");
    gameCanv.classList.add("gameView");
    gameCanv.width = 335;
    gameCanv.height = 422;

    // HACK: interactHandler triggers a re-render, and timer rendering requires the timer handler be set up,
    // so the timer handler needs to be registered before the interact for the necessary data to exist on the first execution of the ineract handler.

    // gameCanv.addEventListener("mousedown", (e) => { return timerHandler(e, gameInstance) }, {once : true});
    gameCanv.oncontextmenu = (e) => { return interactHandler(e, gameInstance); }
    gameCanv.addEventListener("mousedown", (e) => { return interactHandler(e, gameInstance) });
    gameCanv.addEventListener("mouseup"  , (e) => { return interactHandler(e, gameInstance) });
    // gameCanv.addEventListener('touchstart', interactHandler); // relic from touch support.. apprently touches issue both touchend and mouseup? doesnt make sense, but convientient.

    // prepare the starting field.
    let fieldState = []
    for (let _ = 0; _ < fieldHeight ; _++) {
        fieldState.push(Array(fieldWidth).fill(0))
    }

    // randomly generate mine placement
    let [mineLayout, mineSeed] = mineGen(fieldWidth, fieldHeight, mineCount, seed);
    // count hints from mine placement
    let mineHints = hintGen(mineLayout);

    let gameInstance = {
        ctx: gameCanv.getContext("2d"),
        fieldState: fieldState, finished: false, lost: false, restartPressed: false,
        mineSeed: mineSeed, mineLayout: mineLayout, mineHints: mineHints,
        fieldWidth: fieldWidth, fieldHeight: fieldHeight, mineCount: mineCount,
        actionRecords: [], playStart: 0
    }

    // /*
    function printer2d(thing) { for (const row of thing) {console.log(row)}}
    // console.log("intial field state:");
    // printer2d(fieldState)
    // console.log("given mine randomisation:");
    // printer2d(mineLayout)
    // console.log("computed mine hints:");
    // printer2d(mineHints)
    // */

    return gameInstance;
}

export async function gameRestart(game) { // WARN: we "restart" a game by deleting the old one and replacing it with a new one. if any changes stylistic or otherwise are made to the original canvas without our knowledge, we will unknowingly overwrite them. issue out of scope :)
    let seed = await get_seed();
    seed = parseInt(seed); // HACK: get_seed sometimes returns "random" indicating we should use a random seed. parseInt for a string yields NaN, which gets caught by the isNaN check below.
    console.log("gameRestart seed:", seed);

    const newGame = gameInit(game.fieldWidth, game.fieldHeight, game.mineCount, isNaN(seed) ? undefined : seed)
    game.ctx.canvas.replaceWith(newGame.ctx.canvas);
    return newGame;
}

function finishGame(game, lost) {
    if (game.finished) return; // HACK:: on each input process, I have a check for whether the game is lost, which triggers finishGame. since actionResolve is overloaded and I cba refactoring, we make sure re-submits dont happen in here.

    game.finished = true;
    game.lost = lost;

    let promis = submit_playthrough(game);
    promis.then((temp) => {console.log("TEMP:", temp); leaderboard_refresh()})
    // if (game.lost) return;

    // const duration = parseInt(game.actionRecords.length > 1 ? (game.actionRecords.at(-1).timestamp - game.actionRecords.at(0).timestamp) : 0)/1000 + "s"
    // if (duration == "0s") return;

    // leaderboard_insert_entry(localStorage.userIDpub, threebv, duration, seed)
}

export function mineGen(fieldWidth, fieldHeight, mineCount, mineSeed=undefined) {
    console.log("mineGen called with seed", mineSeed)
    // TODO: randomisation to ensure a specific number of mines
    if (mineSeed == undefined) mineSeed = Math.floor(Date.now()/1000) // current time in seconds
    let seedIter = mineSeed

    let game = []
    for (let _ = 0; _ < fieldHeight; _++) game.push(Array(fieldWidth).fill(0));

    for (let _ = 0; _ < mineCount; _++) {
        const randProb = (seedIter = seedIter * 16807 % 2147483647) / 2147483646;
        const mineIndex = Math.round((fieldWidth*fieldHeight-1) * randProb)
        const y = mineIndex % fieldWidth, x = Math.round(mineIndex / fieldHeight)
        // console.log("indexes:", x, y);
        if (game[y][x] == 0) game[y][x] = 1;
        else _ -= 1
    }30-3

    return [game, mineSeed];
}

export function hintGen(mineLayout) {
    let hints = []
    for (const row of mineLayout) {hints.push(Array(row.length).fill(0))}

    for (let y = 0 ; y < mineLayout.length ; y++) {
        for (let x = 0 ; x < mineLayout[0].length ; x++) {
            hints[y][x] = ((mineLayout[y-1]||[])[x-1]||0) + ((mineLayout[y+0]||[])[x-1]||0) + ((mineLayout[y+1]||[])[x-1]||0) +
                          ((mineLayout[y-1]||[])[x+0]||0)                  +                  ((mineLayout[y+1]||[])[x+0]||0) +
                          ((mineLayout[y-1]||[])[x+1]||0) + ((mineLayout[y+0]||[])[x+1]||0) + ((mineLayout[y+1]||[])[x+1]||0)
        }
    }
    // ^ note: thanks javascript for nice and easy out of bounds fallback to 0 :) I still hate you though...

    return hints;
}

function neighbour_operation(w, h, x, y, fun) {
    for (let yAdj = Math.max(y-1, 0) ; yAdj <= Math.min(y+1, h-1) ; yAdj += 1) // all neighbour y positions
        for (let xAdj = Math.max(x-1, 0) ; xAdj <= Math.min(x+1, w-1) ; xAdj += 1) // all neighbour x positions
            fun(xAdj, yAdj);
}

function cell_reveal(game, x, y) {
    if (game.mineLayout[y][x] == 1) { // if there's a mine, the cell state is now mine (3), otherwise open cell (2)
        game.fieldState[y][x] = 3
        finishGame(game, true);
    }
    else { // the cell is safe
        game.fieldState[y][x] = 2 // mark it as an open cell

        // if the revealed hint shows 0, then auto-open all neighbours.
        // check it for auto-opening of cells numbered 0.
        let candidatesForOpen = [[x, y]]; // a list of cells to check, starting with patient zero.
        while (candidatesForOpen.length > 0) {
            const [xCand, yCand] = candidatesForOpen.pop();
            if (game.mineHints[yCand][xCand] != 0) continue; // if the cell's hint isnt 0, skip opening.

            neighbour_operation(game.fieldWidth, game.fieldHeight, xCand, yCand, (xAdj, yAdj) => { // for each of the cell's neighbours that isnt off the field..
                if (game.fieldState[yAdj][xAdj] == 0) // if the neighbour is closed..
                {
                    game.fieldState[yAdj][xAdj] = 2; // mark as opened
                    candidatesForOpen.push([xAdj, yAdj]); // add newly opened cell to the pool of candidates.
                }
            });
        }
    }
}

function actionResolve(game, action, x, y, timestamp) {
    console.log("got action", action);
    // TODO: different outcomes according to left click, right click, mine underneath, safe underneath, etc.
    // TODO: long press for flagging on mobile?

    let actionRecord = { actionID: action, x: x, y: y, timestamp: timestamp, successful: false }
    // ^ note: the timestamp is the miliseconds relative to when the "context" was created (i.e. ms since document loaded (apparently))
    // since it's relative to a fixed landmark, in processing we can just subtract the timestamp of the first action.

    if (action == 3)
    {
        finishGame(game, false); // note: we dont set "lost" to true, because "lost" actually means "hit a mine" and the variable name isnt indicative.
        game.restartPressed = true;
        actionRecord.successful = true;
    }
    else if (action == 4)
    {
        game.restartPressed = false;

        // HACK: mineGen inside gameRestart should probs be the one whom gets a seed from the server, but I'd need to make it async.. so seed handing is done by main.js and gameRestart instead, so that way I can minimize where I deal with async stuff.
        gameRestart(game).then((newGame) => {renderGame(newGame)})

        // const newGame = gameRestart(game);
        // renderGame(newGame);
        actionRecord.successful = true;
    }
    else if (game.finished) { // game.finished check in the middle, meaning the if clauses below only trigger if the game isnt finished.
        console.log("the game is finished")
    }
    else if (action == 0 && game.fieldState[y][x] == 0) { // if left click for a reveal action, but only if the cell is an un-flagged closed cell. (importantly - the cell isnt flagged (note we disable opening of flagged cells))
        actionRecord.successful = true;
        cell_reveal(game, x, y)
    }
    else if (action == 1 && (game.fieldState[y][x] == 1 || game.fieldState[y][x] == 0)) { // right click on a closed cell will toggle flag
        actionRecord.successful = true;
        game.fieldState[y][x] = game.fieldState[y][x] == 1 ? 0 : 1; // toggle flag state of the cell.
    }
    else if ((action == 1 || action == 2) && game.fieldState[y][x] == 2) { //if it's a right click on an open cell, or a left+right click, and the cell is an open cell with a number.. a chord should trigger.
        actionRecord.successful = true;
        // first count the number of neighbouring flags
        let flaggedNeighbours = 0

        neighbour_operation(game.fieldWidth, game.fieldHeight, x, y, (xAdj, yAdj) => { // for each of the cell's neighbours that isnt off the field..
            if (game.fieldState[yAdj][xAdj] == 1) flaggedNeighbours += 1; // note field state 1 is a flagged cell.
        });
        console.log("flagged neighbours:", flaggedNeighbours)

        // if the neighbouring flags equal the hint number, then open all un-flagged neighbours.
        if (flaggedNeighbours == game.mineHints[y][x])
            neighbour_operation(game.fieldWidth, game.fieldHeight, x, y, (xAdj, yAdj) => { // for each of the cell's neighbours that isnt off the field..
                if (game.fieldState[yAdj][xAdj] == 0) cell_reveal(game, xAdj, yAdj); // if the neighbour is hidden unflagged, then reveal.
            });
    }
    else { console.log("unrecognised action for handling:", action) }

    if (actionRecord.successful) { // if the action was valid and carried out
        // if it's the first user action, sync the timer with it.
        if (game.actionRecords.length == 0) timerLoopHandler(game);

        game.actionRecords.push(actionRecord);
    }

    // WARN: copy+paste from render logic. todo: reduce duplication
    let remainingEmptyCells = 0;
    for (let y2 = 0 ; y2 < game.fieldHeight ; y2 += 1)
        for (let x2 = 0 ; x2 < game.fieldWidth ; x2 += 1)
            if (game.mineLayout[y2][x2] == 0 && game.fieldState[y2][x2] != 2)
                remainingEmptyCells += 1;
    console.log("remaining empty cells:", remainingEmptyCells)

    if (remainingEmptyCells == 0) { finishGame(game, false); }
    renderGame(game);
}



const gridStartX = 24, gridStartY = 110; // note: x:25, y:110 (with 0-based indexing) are the positions for the top-left pixel of the top-left-most cell in our background image.
const gridSquareSize = 32; // the pixel dimensions of a cell for us right now is 32x32.

export function renderGame(game) {
    console.info("rendering");
    placePreloaded(game.ctx, "background", 0, 0);

    // grid rendering
    for (let y = gridStartY ; y < gridStartY+game.fieldHeight*gridSquareSize ; y += gridSquareSize) {
        for (let x = gridStartX ; x < gridStartX+game.fieldWidth*gridSquareSize; x += gridSquareSize) {
            let [cellX, cellY] = pixelToCell(x, y);
            switch (game.fieldState[cellY][cellX]) {
                case 0:
                    placePreloaded(game.ctx, "closedCell", x, y);
                    break;
                case 1:
                    placePreloaded(game.ctx, "flaggedCell", x, y);
                    break;
                case 2:
                    placePreloaded(game.ctx, "hint" + game.mineHints[cellY][cellX] + "Cell", x, y);
                    break;
                case 3:
                    placePreloaded(game.ctx, "mineCell", x, y);
                    break;
                default:
                    console.log("how did this even happen? comaplain to the dev :)");
                    console.log(game.fieldState)
                    console.log(cellX, cellY);
                    console.log(game.fieldState[cellY][cellX])
                    break;
            }
        }
    }

    // counters for mines remaining and timer

    const totalMines = game.mineLayout.reduce((r1, r2) => {return r1.concat(r2)}).reduce((a, b) => {return a+b});
    const flaggedMines = game.fieldState.reduce((r1, r2) => {return r1.concat(r2)}).filter((a) => {return a == 1}).length;
    const minesRemaining = Math.max(totalMines-flaggedMines, 0);

    let msElapsed = 0;

    if (game.finished && game.actionRecords.length > 0) { msElapsed = game.actionRecords.at(-1).timestamp - game.actionRecords.at(0).timestamp }
    else { msElapsed = game.actionRecords.length != 0 ? Date.now() - game.playStart : 0 }
    const secondsElapsed = Math.round(msElapsed/1000);

    // console.log("mines remaining:", minesRemaining);
    // console.log("seconds (and ms) elapsed:", secondsElapsed, "(" + msElapsed + ")");

    const segments = { // segments are addressed in the order: top, top-right, bottom-right, bottom, bottom-left, top-left, centre (i.e. clockwise from the top, and then the centre.)
        0 : [1, 1, 1, 1, 1, 1, 0],
        1 : [0, 1, 1, 0, 0, 0, 0],
        2 : [1, 1, 0, 1, 1, 0, 1],
        3 : [1, 1, 1, 1, 0, 0, 1],
        4 : [0, 1, 1, 0, 0, 1, 1],
        5 : [1, 0, 1, 1, 0, 1, 1],
        6 : [1, 0, 1, 1, 1, 1, 1],
        7 : [1, 1, 1, 0, 0, 1, 0],
        8 : [1, 1, 1, 1, 1, 1, 1],
        9 : [1, 1, 1, 1, 0, 1, 1],
    }

    // spacing notes:
    // first black rectangle offset relative to game frame: x:34, y:32
    // second black rectangle offset relative to game frame: x:223, y:32
    // black rectangle dimensions - 78x46
    // black pixels between digits - 4
    // black pixels between left edge to leftmost segment - 2 (note that pixels between right edge and rightmost segment should also be 2, and should match visually)
    // black pixels between top edge and topmost segment - 2 (similar as above)
    // black pixels between left-most side of left segment and left-most side of right segment - 16
    // black pixels between left-most side of left segment and the center segment - 4
    // segment width (include 1px black border) - 26
    // segments all (almost) touch, with a 1 pixel border. this is true between all edge segments both at corners and the centre splits.
    // sidenote: resolution of segment image file matches other assets, but perceptually the pixels comprising segments are actually half as precise. i.e. one visual pixel makes up 4 actual pixels.
    function render_segment(ctx, x, y, num) {
        // NOTE: this function used to pre-clear the segment area with black before drawing the numbers.
        // for some reason, doing that would mean subsequent calls to render_segment would not render anything.
        // since pre-clearing with black isnt necessary, this issue wasnt investigated further but is usesful to note.
        // ctx.rect(x, y, 78, 46);
        // ctx.fillStyle = "black";
        // ctx.fill();

        let renderable = String(num).padStart(3, "0");
        for (let i = 0 ; i < 3 ; i++) {
            let digit = parseInt(renderable[i]);
            
            placePreloaded(ctx, "edgeSegment"   + (segments[digit][0] ? "On" : "Off"), x+2+ 2, y+2   ,   0); // top
            placePreloaded(ctx, "edgeSegment"   + (segments[digit][1] ? "On" : "Off"), x+2+22, y+2+ 2,  90); // top right
            placePreloaded(ctx, "edgeSegment"   + (segments[digit][2] ? "On" : "Off"), x+2+22, y+2+22,  90); // bottom right
            placePreloaded(ctx, "edgeSegment"   + (segments[digit][3] ? "On" : "Off"), x+2+20, y+2+42, 180); // bottom
            placePreloaded(ctx, "edgeSegment"   + (segments[digit][4] ? "On" : "Off"), x+2   , y+2+40, 270); // bottom left
            placePreloaded(ctx, "edgeSegment"   + (segments[digit][5] ? "On" : "Off"), x+2   , y+2+20, 270); // top left
            placePreloaded(ctx, "centerSegment" + (segments[digit][6] ? "On" : "Off"), x+2+ 4, y+2+18,   0); // center

            x += 26;
        }
    }

    render_segment(game.ctx,  34, 32, minesRemaining);
    render_segment(game.ctx, 223, 32, secondsElapsed);

    // restart button rendering
    placePreloaded(game.ctx, (game.lost ? "sad" : "smile") + (game.restartPressed ? "Blink" : "Idle"), 141, 30);
}

function pixelToCell(x, y) {
    x = Math.floor((x - gridStartX)/gridSquareSize)
    y = Math.floor((y - gridStartY)/gridSquareSize)
    return [x, y]
}

let mainDown = false;
let altDown = false;
export function interactHandler(e, game) {
    let justChanged = "none";
    let currentX=0, currentY=0;

    if (e.type == "mousedown" || e.type == "mouseup") {
        currentX = e.offsetX;
        currentY = e.offsetY;

        if (e.button == 0) mainDown = e.type == "mousedown";
        if (e.button == 2) altDown = e.type == "mousedown";
        justChanged = (e.button == 0) ? "main" : "alt"
    }
    else if (e.type == "touchstart") {
        const touch = e.touches[0]
        currentX = touch.offsetX;
        currentY = touch.offsetY;
        justChanged = "main"
    }
    else if (e.type == "contextmenu") {
        currentX = e.offsetX;
        currentY = e.offsetY;
        justChanged = "context"
    }
    else { console.log("panic! we've been given a non-mouse non-touch event! how did this happen :("); }

    // click detection on the reset button
    if (justChanged == "main" && currentX >= 141 && currentX <= 192 && currentY >= 30 && currentY <= 81)
    {
        if (mainDown) actionResolve(game, 3, -1, -1, e.timeStamp); // action id 3 is restart button clicked
        else actionResolve(game, 4, -1, -1, e.timeStamp); // action id 4 is restart button released
        return;
    }

    const [x, y] = pixelToCell(currentX, currentY);

    console.log("translated", currentX, currentY, "to", x, y);
    console.log("mainDown?", mainDown, "altDown?", altDown);

    if (!(x >= 0 && x < game.fieldWidth && y >= 0 && y < game.fieldHeight)) return;

    if (mainDown && !altDown && justChanged == "main") actionResolve(game, 0, x, y, e.timeStamp); // left click action. only opens.
    else if (!mainDown && altDown && justChanged == "alt") actionResolve(game, 1, x, y, e.timeStamp); // right click action. either toggles flag or triggers a chord.
    else if (mainDown && altDown && (justChanged == "alt" || justChanged == "main")) actionResolve(game, 2, x, y, e.timeStamp); // chord action for left+right click.
    else if (!altDown && justChanged == "context") actionResolve(game, 1, x, y, e.timeStamp); // long-press action is the same as a right click.

    // if ((mainDown || altDown) && (justChanged == "main" || justChanged == "alt")) actionResolve(game, mainDown ? (altDown ? 2 : 0) : 1, x, y, e.timeStamp); // HACK: if the mainDown conditional fails, then implicitly altDown must be true since mainDown || altDown was true;
    // else if (justChanged == "context" && !altDown) {
    //     actionResolve(game, 1, x, y, e.timeStamp);
    // }

    return false; // need to return false so the default context menu doesnt show up

}

export function timerLoopHandler(game) {
    game.playStart = Date.now() // event timestamps are relative to context creation (in this case meaning page load), but we want to use epoch time. We store the epoch for the first ever event, as a reference point.
    // the only goal here is to be regularly re-rendering the game every second, to update the timer display.
    // HACK: maybe change to re-render timer only, instead of the whole board. as it is, it's wastefully re-rendering everything, but the performance impact probably wont be noticed at this scale.
    setInterval(() => {if (!game.finished) {renderGame(game)}}, 1000);
}
