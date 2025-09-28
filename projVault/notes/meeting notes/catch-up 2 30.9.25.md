### realisation -  ms dataset necessary
will definitely need to make a minesweeper dataset; none exist.

small random levels of fixed size, aiming for a short solve time

an important metric will be how long someone spent on a particular part of the board,
so levels should be big enough to necessitate focusing on the level in parts.
^ hence, the experiment tool should only let the participant play a small area of the field, and require them to scroll.

other metrics should include perceived difficulty (easy <--> hard) and enjoyment (boring <--> engaging)

### in the scope of the whole semester.. goals include:
interim report
experiment platform created and released
minizinc model created, using these statistics, replicating human playing

##### goal planning
there's about 10 weeks until the interim report.. (due week 12)

| week(s)           | goal                                                                                                                                                |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2 (this week)     | I'd want to finish planning what this dataset needs to contain                                                                                      |
| 3, 4, 5           | implement minesweeper test platform                                                                                                                 |
| 6, 7              | (while data is being collected..)<br>planning and preparing data analysis<br>(deciding what to do with it; how to analyse it; how it can be useful) |
| 8, 9, 10          | write-up of interim report                                                                                                                          |
| 11, 12            | planning + implementation of "human-like" minizinc model<br>(or at least the parts that'd be good to include in interim report )                    |
| until sem 2 start | finish human-like mz model                                                                                                                          |

## paper readings update
didnt read as much as I was hoping.. only looked over the procedural mario paper.
###### WMP Reis et al.'s procedural mario
the paper u sent to me also used human-annotated levels,
but focuses more on combining mini levels together to form cohesive larger levels and create a storyline
since minesweeper fields have no story, there wasnt much in their methodology I could apply

## knowledge gaps:
unsure if minizinc models are suited for trying to replicate human thinking.
I'll want to find some papers that have already tried to tweak minizinc models to replicate humans,
ideally this happens on monday and I delete this paragraph and replace it with my findings before you read this.