import {placePreloaded} from "/modules/helpRender.js"

export function mineGen() {
    return [[0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0]]
}

export function hintGen(mineLayout) {
    return [[0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 2, 2, 1, 0, 0, 0],
            [0, 0, 2, 2, 2, 1, 0, 0, 0],
            [0, 0, 2, 2, 3, 1, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0]]
}

function actionResolve(ctx, fieldState, mineLayout, mineHints, startTime, fieldWidth, fieldHeight, action, x, y) {
    console.log("action came in")
    console.log("test:", JSON.stringify(fieldState))
    // TODO: different outcomes according to left click, right click, mine underneath, safe underneath, etc.
    // TODO: long press for flagging on mobile?

    if (action == 0 && fieldState[y][x] != 1) { // if left click for a reveal action, AND the cell isnt flagged (note we disable opening of flagged cells)
        // fieldState[y][x] = (mineLayout[y][x] == 1) ? 3 : 2 // if there's a mine, the cell state is now mine (3), otherwise open cell (2)
        var temp = (mineLayout[y][x] == 1) ? 3 : 2 // if there's a mine, the cell state is now mine (3), otherwise open cell (2)
    }
    else if (action == 1) { // right click for a toggle flag
        // fieldState[y][x] = fieldState[y][x] == 1 ? 0 : 1; // toggle flag state of the cell.
        var temp = fieldState[y][x] == 1 ? 0 : 1; // toggle flag state of the cell.
    }
    fieldState[y][x] = temp;
    console.log("to update:", fieldState[y][x])
    console.log("temp", temp)
    console.log("2est:", JSON.stringify(fieldState))

    console.log("action updated")
    renderGame(ctx, fieldState, mineLayout, mineHints, startTime, fieldWidth, fieldHeight);
    console.log("rerendered")
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
                    placePreloaded(ctx, "hint" + mineHints[cellX][cellY] + "Cell", x, y);
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
    if (e.type == "mouseup") {
        var currentX = e.offsetX;
        var currentY = e.offsetY;
    }
    else if (e.type == "touchend") {
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

