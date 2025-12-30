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

function actionResolve(fieldState, x, y) {
    // TODO: different outcomes according to left click, right click, mine underneath, safe underneath, etc.
}



const gridStartX = 24, gridStartY = 110; // note: x:25, y:110 (with 0-based indexing) are the positions for the top-left pixel of the top-left-most cell in our background image.
const gridSquareSize = 32; // the pixel dimensions of a cell for us right now is 32x32.

export function renderGame(ctx, fieldState, mineHints, startTime, fieldWidth, fieldHeight) {
    placePreloaded(ctx, "background", 0, 0);

    for (let cellY = gridStartY ; cellY < gridStartY+fieldHeight*gridSquareSize ; cellY += gridSquareSize) {
        for (let cellX = gridStartX ; cellX < gridStartX+fieldWidth*gridSquareSize; cellX += gridSquareSize) {
            placePreloaded(ctx, "closedCell", cellX, cellY);
        }
    }
}

function pixelToCell(x, y) {
    console.log(x, y)
    x = Math.floor((x - gridStartX)/gridSquareSize)
    y = Math.floor((y - gridStartY)/gridSquareSize)
    return [x, y]
}
export function interactHandler(e, ctx, fieldState) {
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

    actionResolve(fieldState, x, y);
}

