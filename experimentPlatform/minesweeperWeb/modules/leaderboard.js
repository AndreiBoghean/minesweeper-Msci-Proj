import {get_leaderboard} from "/modules/apiWrapper.js"

export async function leaderboard_refresh() {
    const leaderboardEntries = await get_leaderboard();

    console.log("lb entries:", leaderboardEntries);

    const lb = document.getElementById("leaderboard");

    for (const entry of leaderboardEntries) {
        const txt = document.createTextNode(JSON.stringify(entry))
        lb.appendChild(txt);

        const button = document.createElement("button");
        button.innerHTML = "attempt?";
        button.onclick = () => { 
            let urlParams = new URLSearchParams(window.location.search);
            urlParams.set("seed", entry.seed);

            window.location.href = window.location.origin + window.location.pathname + "?" + urlParams.toString()
        }
        lb.appendChild(button)
        lb.appendChild(document.createElement("br"))
    }
}

export function leaderboard_append() {
    
}
