// const fs = require('fs');
import * as fs from 'fs';

const seedPool = [
    1769089904946, // 3BV of 2
    1769089890419, // 3BV of 5
    1769089890390, // 3BV of 7
    1769089890393, // 3BV of 8
    1769089890402, // 3BV of 9
    1769089890404, // 3BV of 10
    1769089890406, // 3BV of 11
    1769089890426, // 3BV of 12
    1769089890391, // 3BV of 13
    1769089890380, // 3BV of 14
    1769089890394, // 3BV of 15
    1769089890387, // 3BV of 16
    1769089890388, // 3BV of 17
    1769089890444, // 3BV of 18
    1769089890461, // 3BV of 19
    1769089890420, // 3BV of 20
    1769089890408, // 3BV of 22
    1769089890446, // 3BV of 26
    1769089890521, // 3BV of 30
    1769089891879, // 3BV of 35
    1769089892886, // 3BV of 40
]

function mineGen(fieldWidth, fieldHeight, mineCount, mineSeed) {
    let seedIter = mineSeed

    let game = []
    for (let _ = 0; _ < fieldHeight; _++) game.push(Array(fieldWidth).fill(0));

    for (let _ = 0; _ < mineCount; _++) {
        const randProb = (seedIter = seedIter * 16807 % 2147483647) / 2147483646;
        const mineIndex = Math.round((fieldWidth*fieldHeight-1) * randProb)
        const y = mineIndex % fieldWidth, x = Math.round(mineIndex / fieldHeight)
        // console.log("indexes:", x, y);
        if (game[y][x] == 0) game[y][x] = 1;
        else _ -= 1
    }

    return game;
}


let data = {}
for (const seed of seedPool)
    data[seed] = mineGen(9, 9, 10, seed);

const jsonData = JSON.stringify(data); // null and 2 are used for pretty-printing

fs.writeFile('seedRenders.json', jsonData, (err) => {
    if (err) {
        console.error("Error writing file:", err);
        return;
    }
    console.log("File has been written successfully!");
});
