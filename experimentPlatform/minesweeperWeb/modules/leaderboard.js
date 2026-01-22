import {get_leaderboard} from "/modules/apiWrapper.js"

export function leaderboard_insert_entry(userID, threebv, duration, seed) {
    const lbTable = document.getElementById("lbTable");

    const row = document.createElement("tr");
    lbTable.appendChild(row)

    const userH = document.createElement("td");
    const tH = document.createElement("td");
    const tbvH = document.createElement("td");
    const attempt = document.createElement("td");
    userH.innerHTML = userID;
    tbvH.innerHTML = threebv;
    tH.innerHTML = duration;
    row.appendChild(userH);
    row.appendChild(tH);
    row.appendChild(tbvH);
    row.appendChild(attempt);


    const button = document.createElement("button");
    button.innerHTML = "attempt?";
    button.onclick = () => { 
        let urlParams = new URLSearchParams(window.location.search);
        urlParams.set("seed", seed);

        window.location.href = window.location.origin + window.location.pathname + "?" + urlParams.toString()
    }
    attempt.appendChild(button)
}

export async function leaderboard_refresh() {
    const leaderboardEntries = await get_leaderboard();
    console.log("lb entries:", leaderboardEntries);

    const lbWrap = document.getElementById("leaderboardWrap");
    lbWrap.innerHTML = "" // empty children

    const usernameSet = document.createElement("button");
    usernameSet.innerHTML = "set<br/>username"
    usernameSet.style = "float: right;"
    usernameSet.onclick = () => { localStorage.userIDpub = prompt("set username?") || localStorage.userIDpub; leaderboard_refresh(); }
    lbWrap.appendChild(usernameSet)

    const p = document.createElement("p");
    p.appendChild(document.createTextNode("your username:"))
    p.appendChild(document.createElement("br"))
    p.appendChild(document.createTextNode(localStorage.userIDpub))
    lbWrap.appendChild(p)

    const lbTable = document.createElement("table");
    lbTable.id = "lbTable"
    lbWrap.appendChild(lbTable);

    const tableHeader = document.createElement("tr");
    lbTable.appendChild(tableHeader);
    const th1 = document.createElement("th")
    const th2 = document.createElement("th")
    const th3 = document.createElement("th")
    const th4 = document.createElement("th")
    th1.innerHTML = "userID"
    th2.innerHTML = "time"
    th3.innerHTML = "3BV"
    tableHeader.appendChild(th1);
    tableHeader.appendChild(th2);
    tableHeader.appendChild(th3);
    tableHeader.appendChild(th4);

    console.log("leaderboard entries:", leaderboardEntries)
    for (const entry of leaderboardEntries) {
        if (!entry.successful) continue;

        const userID = entry.userIDpub
        const threebv = entry.threebv
        const duration = parseInt(entry.duration)/1000 + "s"

        if (duration == "0s") continue;

        leaderboard_insert_entry(userID, threebv, duration, entry.seed)
    }
}
