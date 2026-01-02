import {placePreloaded} from "/modules/helpRender.js"

export function mineGen(fieldWidth, fieldHeight) {
    // TODO: randomisation to ensure a specific number of mines
    const mineSeed = Math.floor(Date.now()/1000) // current time in seconds
    let seedIter = mineSeed

    var game = []
    for (let y = 0 ; y < fieldHeight ; y++) {
        let row = []
        for (let x = 0 ; x < fieldWidth; x++) {
            row.push((seedIter = seedIter * 16807 % 2147483647) < (0.2*2147483646) ? 1 : 0); // PRNG sourced from https://gist.github.com/blixt/f17b47c62508be59987b
        }
        game.push(row)
    }

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

    if (action == 0 && game.fieldState[y][x] == 0) { // if left click for a reveal action, but only if the cell is an un-flagged closed cell. (importantly - the cell isnt flagged (note we disable opening of flagged cells))
        actionRecord.successful = true;
        cell_reveal(game, x, y)
    }
    else if (action == 1 && (game.fieldState[y][x] == 1 || game.fieldState[y][x] == 0)) { // right click for a toggle flag
        game.fieldState[y][x] = game.fieldState[y][x] == 1 ? 0 : 1; // toggle flag state of the cell.
        actionRecord.successful = true;
    }
    else if (action == 2 && game.fieldState[y][x] == 2) { // if the action is a left+right click, and the cell is an open cell with a number..
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

    game.actionRecords.push(actionRecord);
    renderGame(game);
}



const gridStartX = 24, gridStartY = 110; // note: x:25, y:110 (with 0-based indexing) are the positions for the top-left pixel of the top-left-most cell in our background image.
const gridSquareSize = 32; // the pixel dimensions of a cell for us right now is 32x32.

export function renderGame(game) {
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

    const msElapsed = game.actionRecords.length != 0 ? Date.now() - game.playStart : 0;
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
}

function pixelToCell(x, y) {
    x = Math.floor((x - gridStartX)/gridSquareSize)
    y = Math.floor((y - gridStartY)/gridSquareSize)
    return [x, y]
}

let leftDown = false;
let rightDown = false;
export function interactHandler(e, game) {
    if (e.type == "mousedown") {
        var currentX = e.offsetX;
        var currentY = e.offsetY;

        if (e.button == 0) leftDown = true;
        if (e.button == 2) rightDown = true;
    }
    else if (e.type == "mouseup") { // we dont execute any actions on mouseup, so getting currentXY isnt necessary.
        if (e.button == 0) leftDown = false;
        if (e.button == 2) rightDown = false;
    }
    else if (e.type == "touchstart") {
        let touch = e.touches[0]
        var currentX = touch.offsetX;
        var currentY = touch.offsetY;
    }
    else { console.log("panic! we've been given a non-mouse non-touch event! how did this happen :("); }

    // TODO: this assumes mouse.. touch wont support flagging right now.
    if (e.type != "mousedown" || (!leftDown && !rightDown)) return;

    const [x, y] = pixelToCell(currentX, currentY);
    console.log(x, y)
    console.log(e)
    console.log("leftDown?", leftDown, "rightDown?", rightDown);

    actionResolve(game, leftDown ? (rightDown ? 2 : 0) : 1, x, y, e.timeStamp); // HACK: if the leftDown conditional fails, then implicitly rightDown must be true, because the return above didnt trigger.
}

export function timerHandler(e, game) {
    game.playStart = Date.now() // event timestamps are relative to context creation (in this case meaning page load), but we want to use epoch time. We store the epoch for the first ever event, as a reference point.
    // the only goal here is to be regularly re-rendering the game every second, to update the timer display.
    // HACK: maybe change to re-render timer only, instead of the whole board. as it is, it's wastefully re-rendering everything, but the performance impact probably wont be noticed at this scale.
    setInterval(() => {renderGame(game)}, 1000);
}
