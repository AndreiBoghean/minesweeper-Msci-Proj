import {placePreloaded} from "/modules/helpRender.js"

export function mineGen(fieldWidth, fieldHeight) {
    // TODO: randomisation to ensure a specific number of mines
    // TODO: seed randomisation with field generation time, so we can re-produce a playthrough from the time it was started.
    var game = []
    for (let y = 0 ; y < fieldHeight ; y++) {
        let row = []
        for (let x = 0 ; x < fieldWidth; x++) {
            row.push(Math.random() < 0.2 ? 1 : 0);
        }
        game.push(row)
    }

    return game;
    return [[0, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0]]
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
    return [[0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0]]
}

function actionResolve(ctx, fieldState, mineLayout, mineHints, startTime, fieldWidth, fieldHeight, action, x, y) {
    console.log("action came in")
    console.log("test:", JSON.stringify(fieldState))
    // TODO: different outcomes according to left click, right click, mine underneath, safe underneath, etc.
    // TODO: long press for flagging on mobile?

    if (action == 0 && fieldState[y][x] == 0) { // if left click for a reveal action, but only if the cell is an un-flagged closed cell. (importantly - the cell isnt flagged (note we disable opening of flagged cells))
        // fieldState[y][x] = (mineLayout[y][x] == 1) ? 3 : 2 // if there's a mine, the cell state is now mine (3), otherwise open cell (2)
        fieldState[y][x] = (mineLayout[y][x] == 1) ? 3 : 2 // if there's a mine, the cell state is now mine (3), otherwise open cell (2)
    }
    else if (action == 1 && (fieldState[y][x] == 1 || fieldState[y][x] == 0)) { // right click for a toggle flag
        // fieldState[y][x] = fieldState[y][x] == 1 ? 0 : 1; // toggle flag state of the cell.
        fieldState[y][x] = fieldState[y][x] == 1 ? 0 : 1; // toggle flag state of the cell.
    }

    renderGame(ctx, fieldState, mineLayout, mineHints, startTime, fieldWidth, fieldHeight);
}



const gridStartX = 24, gridStartY = 110; // note: x:25, y:110 (with 0-based indexing) are the positions for the top-left pixel of the top-left-most cell in our background image.
const gridSquareSize = 32; // the pixel dimensions of a cell for us right now is 32x32.

export function renderGame(ctx, fieldState, mineLayout, mineHints, startTime, fieldWidth, fieldHeight) {
    placePreloaded(ctx, "background", 0, 0);

    for (let y = gridStartY ; y < gridStartY+fieldHeight*gridSquareSize ; y += gridSquareSize) {
        for (let x = gridStartX ; x < gridStartX+fieldWidth*gridSquareSize; x += gridSquareSize) {
            let [cellX, cellY] = pixelToCell(x, y);
            switch (fieldState[cellY][cellX]) {
                case 0:
                    placePreloaded(ctx, "closedCell", x, y);
                    break;
                case 1:
                    placePreloaded(ctx, "flaggedCell", x, y);
                    break;
                case 2:
                    placePreloaded(ctx, "hint" + mineHints[cellY][cellX] + "Cell", x, y);
                    break;
                case 3:
                    placePreloaded(ctx, "mineCell", x, y);
                    break;
                default:
                    console.log("how did this even happen? comaplain to the dev :)");
                    console.log(fieldState)
                    console.log(cellX, cellY);
                    console.log(fieldState[cellY][cellX])
                    break;
            }
        }
    }
}

function pixelToCell(x, y) {
    x = Math.floor((x - gridStartX)/gridSquareSize)
    y = Math.floor((y - gridStartY)/gridSquareSize)
    return [x, y]
}
export function interactHandler(e, ctx, fieldState, mineLayout, mineHints, startTime, fieldWidth, fieldHeight) {
    if (e.type == "mousedown") {
        var currentX = e.offsetX;
        var currentY = e.offsetY;
    }
    else if (e.type == "touchstart") {
        let touch = e.touches[0]
        var currentX = touch.offsetX;
        var currentY = touch.offsetY;
    }
    else { console.log("panic! we've been given a non-mouse non-touch event! how did this happen :("); }

    const [x, y] = pixelToCell(currentX, currentY);
    console.log(x, y)
    console.log(e)

    // TODO: this assumes mouse.. touch wont support flagging right now.
    if (e.button == 0 || e.button == 2) actionResolve(ctx, fieldState, mineLayout, mineHints, startTime, fieldWidth, fieldHeight, e.button == 0 ? 0 : 1, x, y);
    // ^ note: we ignore events that arent left or right click
}

