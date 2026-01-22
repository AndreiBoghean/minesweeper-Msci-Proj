// const backend_endpoint = "http://localhost:3000"
// const backend_endpoint = "http://192.168.0.51:3081"
// const backend_endpoint = "http://192.168.0.224:3081"
const backend_endpoint = "https://msAPI.andreiboghean.com"

// TODO: check for 200 status codes on api requests?

// HACK: matrix helper function, duplicated in game.js
function neighbour_operation(w, h, x, y, fun) {
    for (let yAdj = Math.max(y-1, 0) ; yAdj <= Math.min(y+1, h-1) ; yAdj += 1) // all neighbour y positions
        for (let xAdj = Math.max(x-1, 0) ; xAdj <= Math.min(x+1, w-1) ; xAdj += 1) // all neighbour x positions
            fun(xAdj, yAdj);
}

export function submit_playthrough(game) {
    console.info("submitting playthrough")
    const userIDpriv = localStorage.userIDpub;
    const userIDpub = localStorage.userIDpub;
    const timestamp = game.playStart;
    const seed = game.mineSeed;
    const actionRecords = game.actionRecords;

    let duration = game.actionRecords.length > 1 ? (game.actionRecords.at(-1).timestamp - game.actionRecords.at(0).timestamp) : 0;

    // 3bv calculated as (all squares) minus (mine count)
    let threebv = game.fieldWidth*game.fieldHeight;
    let unclickables = [];
    for (let y=0 ; y < game.fieldWidth ; y++)
        for (let x=0 ; x < game.fieldWidth ; x++) {
            const i = (y+1)*game.fieldWidth+x;

            if (unclickables.includes(i))
                continue;

            else if (game.mineHints[y][x] == 0 && game.mineLayout[y][x] == 0) { // if cell is a non-mine with an empty hint
                console.log("didnt skip", x, y)
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
    console.log("unclickables:", unclickables);
    threebv -= unclickables.length;

    // console.log("thing1", (game.fieldWidth*game.fieldHeight));
    // console.log("thing1", (game.mineHints.reduce((r1, r2) => {return r1.concat(r2)})));
    // console.log("thing1", (game.mineCount));
    // let threebv = (game.fieldWidth*game.fieldHeight) - (game.mineHints.reduce((r1, r2) => {return r1.concat(r2)}).filter(c => c == 0).length) - (neighboursEmpty.length) - (game.mineCount);
    console.log("calculated 3bv", threebv)

    const constructed_url = backend_endpoint + "/postSolve?userIDpub=" + userIDpub + "&userIDpriv=" + userIDpriv + "&timestamp=" + timestamp + "&duration=" + duration + "&successful=" + (game.finished && !game.lost) + "&seed=" + seed + "&threebv=" + threebv
    let promis = fetch(constructed_url, {
        method: "POST",
        body: JSON.stringify(actionRecords),
        headers: { "Content-type": "application/json; charset=UTF-8" }
    });
    promis = promis.then((response) => console.log("got playthrough response of", response));

    return promis;
}

export async function get_leaderboard() {
    console.log("trying")
    const response = await fetch(backend_endpoint + "/listSolves", { method: "GET" })
    console.log("what")
    console.log("more what", response)
        return await response.json()
}
