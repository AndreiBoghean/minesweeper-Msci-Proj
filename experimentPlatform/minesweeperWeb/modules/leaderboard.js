import {get_leaderboard} from "/modules/apiWrapper.js"

export async function leaderboard_refresh() {
    const leaderboardEntries = await get_leaderboard();
    console.log("lb entries:", leaderboardEntries);

    const lb = document.getElementById("leaderboard");
    lb.innerHTML = "" // empty children

    lb.appendChild(document.createTextNode("leaderboard:"))
    lb.appendChild(document.createTextNode("your username: " + localStorage.userIDpub))

    const usernameSet = document.createElement("button");
    usernameSet.innerHTML = "set username"
    usernameSet.style = "float: right;"
    usernameSet.onclick = () => { localStorage.userIDpub = prompt("test") || localStorage.userIDpub; leaderboard_refresh(); }
    lb.appendChild(usernameSet)
    lb.appendChild(document.createElement("br"))

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
