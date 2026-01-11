import { MongoClient } from "mongodb"
import express from "express"

// mongodb database setup // TODO: abstract mongoDB and express routing to different modules?

function argOrDefault(arg, defu) {
    for (let i=0 ; i < process.argv.length ; i++)
        if (process.argv[i] == arg && process.argv.length > i+1) {
            return process.argv[i+1];
        }
    
    return defu;
}

let dbUrl = argOrDefault("--mongoEndpoint", "mongodb://localhost:27017");
const client = new MongoClient(dbUrl);

client.connect();
console.log("Connected successfully to database server");

const db = client.db("developmentDB");
const collection = db.collection("documents");

// express network routing configuration
// TODO: support HTTPS
const app = express()
const port = parseInt(argOrDefault("--port", "3000"));

app.use(express.text()) // tell the middleware to allow and parse Content-Type: text/plain // (mainly for testing purposes)
app.use(express.json()) // tell the middleware to allow and parse Content-Type: application/json

app.use(function (req, res, next) {
    res.setHeader("Access-Control-Allow-Origin", argOrDefault("--allowedOrigin", "*")); // WARN: change this to the deployment domain when you deploy.
    res.setHeader("Access-Control-Allow-Methods", "GET, POST");
    res.setHeader("Access-Control-Allow-Headers", "X-Requested-With,content-type");

    next();
});

app.get("/", (req, res) => {
    res.send("Hello World!!! you wanted:" + req.query.hithere)
})

app.get("/listSolves", async (req, res) => { // NOTE: no input validation should be needed here.
    const projectFields = { _id: 0, userID: 1, timestamp: 1, seed: 1, duration: 1, threebv: 1 };
    const result = await collection.find().project(projectFields).toArray();
    console.log("found existing solves", result);

    res.send(result);
})

app.post("/postSolve", async (req, res) => {
    // assumes a well-formed request... TODO: input validation
    const userAgent = req.get("User-Agent");
    const userID = req.query.userID; // expected as string.
    const timestamp = req.query.timestamp; // expected as unix time, but a different timestamp from the seed.
    const duration = req.query.duration; // expected as miliseconds.
    const seed = req.query.seed; // expected as unix time.
    const threebv = req.query.threebv;
    const body = req.body;

    const actionRecords = body; // TODO: parse action records to check for funny business and the likes (also todo: learn what's good practice)

    console.log("got user agent", userAgent);
    console.log("got userID", userID);
    console.log("got timestamp", timestamp);
    console.log("got duration", duration);
    console.log("got seed", seed);
    console.log("got threebv", threebv);
    console.log("got actionRecords", actionRecords);

    res.send("post recieved");

    const submissionRecord = {userAgent: userAgent, userID: userID, seed: seed, threebv: threebv, timestamp: timestamp, duration: duration, actionRecords: actionRecords}
    const result = await collection.insertOne(submissionRecord)
    console.log("inserted new submission", submissionRecord)
    console.log("obtained result", result)
})

/* NOTE: gave up on making a client-side replay and analysis page for submissions, so there's no longer a need to query full solves.

app.get("/getSolve", async (req, res) => {
    const userID = req.query.userID; // expected as string.
    const timestamp = req.query.timestamp; // expected as unix time, but a different timestamp from the seed.
    const seed = req.query.seed; // expected as unix time

    console.log("got userID", userID);
    console.log("got timestamp", timestamp);
    console.log("got seed", seed);

    const primaryKey = {userID: userID, timestamp: timestamp, seed: seed}

    const projectFields = { _id: 0, userID: 1, timestamp: 1, seed: 1, duration: 1, threebv: 1 };

    switch (req.query.solveFormat) {
        case "core":
            projectFields = { _id: 0, userID: 1, timestamp: 1, seed: 1, actionRecords: 1 };
            console.log("using projection for core")
            break;
        case "regular":
            projectFields = { _id: 0, userID: 1, timestamp: 1, seed: 1, actionRecords: 1, threebv: 1, timestamp: 1, solveTime: 1 };
            console.log("using projection for regular")
            break;
        case "investigated":
            projectFields = { _id: 0, userID: 1, timestamp: 1, seed: 1, actionRecords: 1, threebv: 1, timestamp: 1, solveTime: 1, RAC: 1 };
            console.log("using projection for investigated")
            break;
        default:
            console.log("unrecognised query parameter :(")
            res.status(400).send("Error 400: unrecognised query parameter")
            break;
    }

    const result = await collection.findOne(primaryKey, {projection: projectFields});
    console.log("found match for", primaryKey, "as", result);

    res.send(result);
})
*/

app.listen(port, () => {
    console.log(`minesweeper database backend listening on port ${port}`)
})

/* OLD DATABASE RUMINATIONS
ok what do we need in the database?

we have various forms for a submitten run.
1. the minimal representation of a run - what we get in a run submission
2. the processed representation for a run - minimal with further sugar calculations for 3BV, playthrough duration
3. the more processed representation - as above, but with processing for relational arc conistency. this is an extra stretch goal you will do this weekend :)
on top of these, we need a variant of form 1. which is a preview for the leaderboard.

these forms, in order of size, are 1: solve preview, 2 solve core, 3 solve regular, 4 solve investigated
(names are subject to change.. and purely to keep myself entertained internally..)

what actually are in these?

we start with solve core.
the data needs to include all information necessary to uniquely identify the run.
this should be user agentID, timestamp, seed - THE SOLVE PRIMARY KEY(s)
on top, we also have the actual solve data - the action record list.

then, we consider preview.
simply, it will be the solve PK as before (user agentID, timestamp, seed)
with some other info on top we got from processing
(solve time, 3BV)

we need to support the following flows:
1. loading database on website load
    - takes nothing (maybe size to return? and a sort?)
    - returns a solve preview
2. submitting a run (and subsequent refresh)
    - takes a `solve core` (userID, timestamp, seed, actionRecords).
    - returns nothing
    - leads to processing of additional information i.e. 3BV, RAC, and solve duration
3. loading an instance for attempt
    - NO API SUPPORT for this, since the `solve preview` already includes the seed, which is all that's needed to faciliate a re-attempt
4. loading an instance for review
    - either the `solve regular`, or eventually the `solve investigated` when we implement RAC.

all of this comprises a main table of run submissions.
in addition, however, we'll also want a table mapping provided user IDs to user agent strings or whatever else we use for fingerprinting
why do we use fingerprinting? to not shove login pages in the face of the users :) they will however be optionally able to dawn a username, which we'll use for the leaderboard rather than it being anonymised.
TODO: maybe allow private submissions, so ppl can give us data without the pressure of competing on the leaderboard?
*/
