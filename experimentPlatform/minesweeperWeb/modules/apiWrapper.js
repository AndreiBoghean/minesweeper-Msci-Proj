//const backend_endpoint = "http://localhost:3000"
// const backend_endpoint = "http://192.168.0.51:3081"
// const backend_endpoint = "http://192.168.0.224:3081"
const backend_endpoint = "https://msAPI.andreiboghean.com"

import {calculate3BV} from "/modules/game.js"

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
    const threebv = calculate3BV(game);


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
    const response = await fetch(backend_endpoint + "/listSolves", { method: "GET" })
    return await response.json()
}


export async function get_seed() {
    const response = await fetch(backend_endpoint + "/getRandomSeed", { method: "GET" })
    console.log("seed response:", response)
    if (response.status != 200) return "random";
    return (await response.text())
}
