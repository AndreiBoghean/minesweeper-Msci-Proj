// const backend_endpoint = "http://localhost:3000"
// const backend_endpoint = "http://192.168.0.51:3081"
const backend_endpoint = "http://192.168.0.224:3081"
// const backend_endpoint = "https://msAPI.andreiboghean.com"


// TODO: check for 200 status codes on api requests?

export function submit_playthrough(game) {
    console.log("submitting playthrough")
    const userID = "devID";
    const timestamp = game.playStart;
    const seed = game.mineSeed;
    const actionRecords = game.actionRecords;

    fetch(backend_endpoint + "/postSolve?userID=" + userID + "&timestamp=" + timestamp + "&seed=" + seed, {
        method: "POST",
        body: JSON.stringify(actionRecords),
        headers: { "Content-type": "application/json; charset=UTF-8" }
    })
      .then((response) => console.log("got playthrough response of", response));
}

export async function get_leaderboard() {
    console.log("trying")
    const response = await fetch(backend_endpoint + "/listSolves", { method: "GET" })
    console.log("what")
    console.log("more what", response)
        return await response.json()
}
