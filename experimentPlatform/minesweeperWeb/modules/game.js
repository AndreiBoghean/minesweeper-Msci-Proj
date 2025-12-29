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



const gridStartX = 24, gridStartY = 110; // note: x:25, y:110 (with 0-based indexing) are the positions for the top-left pixel of the top-left-most cell in our background image.
const gridSquareSize = 32; // the pixel dimensions of a cell for us right now is 32x32.

export function renderGame(ctx, fieldState, mineHints, startTime, fieldWidth, fieldHeight) {
    placePreloaded(ctx, "background", 0, 0);

    for (let cellY = gridStartY ; cellY < gridStartY+fieldHeight*gridSquareSize ; cellY += gridSquareSize) {
        for (let cellX = gridStartX ; cellX < gridStartX+fieldWidth*gridSquareSize; cellX += gridSquareSize) {
            placePreloaded(ctx, "closedCell", cellX, cellY);
            continue;
            let closedCell = document.createElement("img");
            closedCell.src = "/assets/closedCell.png"
            closedCell.onload = () => {
                ctx.drawImage(closedCell, 50, 50);
                console.log("loaded");
            };
            return;
        }
    }
}
