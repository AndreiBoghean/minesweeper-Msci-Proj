#### realisation -  ms dataset necessary
will definitely need to make a minesweeper dataset; none exist.
###### thoughts on what makes a useful ms dataset..
small random levels of fixed size, aiming for a short solve time

an important metric will be how long someone spent on a particular part of the board,
so levels should be big enough to necessitate focusing on the level in parts.
^ hence, the experiment tool should only let the participant play a small area of the field, and require them to scroll.

other metrics should include perceived difficulty (easy <--> hard) and enjoyment (boring <--> engaging)
#### (current) overall project outline
sem 1:
- interim report
- experiment platform needs to be created and released
- breakdown and analysis of data
- minizinc model replicating human behaviour
	- (unclear what this will mean ultimately; real attempts at replicating human playing use an ML model because it makes more sense.)
sem 2:
- a minizinc model with different minesweeper "techniques" (need to research such techniques from ms guides online)
	  -  this approach is demonstrated by [this paper](https://cdn.aaai.org/ocs/2517/2517-11201-1-PB.pdf), so I presume it's not an entirely misguided approach.
	    the paper mentions that backtracking search "is not very relevant to estimating human performance", and suggests constraint propagation instead, particularly because that's how humans naturally solve constraint satisfaction problems

basically, there's 2 parts to this project:
first, building a human-like minizinc model from player data
second, programming this model with different combinations of ms techniques,
to ultimately ascertain the cognitive value of different minesweeper techniques.
##### goal planning
###### semester 1
there's about 10 weeks until the interim report.. (due week 12. it's week 2 now.)

| week(s)           | goal                                                                                                                                                |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2                 | finish planning what this dataset needs to contain                                                                                                  |
| 3, 4              | implement minesweeper test platform                                                                                                                 |
| 5, 6              | (while data is being collected..)<br>planning and preparing data analysis<br>(deciding what to do with it; how to analyse it; how it can be useful) |
| 7, 8, 9           | write-up of interim report                                                                                                                          |
| 11, 12            | planning + implementation of "human-like" minizinc model<br>(or at least the parts that'd be good to include in interim report )                    |
| until sem 2 start | finish human-like mz model                                                                                                                          |

## paper readings update
###### WMP Reis et al.'s procedural mario
this paper used human-annotated levels (similar to what the project would need to do),
but focuses more on combining mini levels together to form cohesive larger levels and create a storyline
since minesweeper fields have no story, there wasnt much in their methodology I could apply

## knowledge gaps:
unsure if minizinc models are suited for trying to replicate human thinking.
I'll want to find some papers that have already tried to tweak minizinc models to replicate humans,
ideally this happens on monday and I delete this paragraph and replace it with my findings before you read this.

refresh: my idea was to, using ms gameplay, create a minizinc model that replicates the human approach
HOWEVER..
replicating human behaviour is typically done via some sort of ML model, because they can simply fit better..
a human person looking at the data and manually inferring patterns and trying to program them into a minizinc model
is (I think) simply inferior.

would this be a valid drawback of the approach to simply "accept" and do it anyways?
and if it yields poor performance, the very least I can do is say that "well clearly this doesnt work. it's obvious now because it's been tried and failed".
I'm aware that would be fairly cheat-y thought.



https://www.nature.com/articles/srep34851.pdf
consideration (from reading that paper ^): in many NP-complete problems, humans can be pretty reliant on randomly choosing a solution and getting lucky (like monte-carlo)
whether this crux is equally effective in minesweeper isnt clear to me. if it is.. I'm not sure how I'd make a model follow that. I'm assuming it would be by choosing a solver that uses monte-carlo?

another important consideration is that KP problems are small-ish, and backtracking can often require re-doing your whole solution if not a large portion.
inversely, in minesweeper, logical errors are rare. the difficulty stems from reading, memorising, and eliminating possible states.
^ this is possible because minesweeper fields are easily separable into distinct sub-problems, whereas knapsack not so much.

my understanding is that, since knapsack cant easily be broken down, humans randomly pick some starter items until the problem is reduced to something easy enough for them to handle
this behaviour still happens in minesweeper, but on much smaller scales. minesweeper is like multiple small kp problems?
.. after further reading of the paper, this seems to be touched on. what I think of as "easy enough to handle" is in fact problems small enough to be tackled by humans using a dp approach.
knapsack problems have to be reduced, whereas minesweeper problems dont need to be reduced, because they support being partitioned (to some degree) instead
.... after even more reading, the paper claims there's no relation between input size and human performance, implying that at no point do humans employ dynamic programming techniques,
.... but to me it seems like kp problems by nature require lots of memory and hence none of their problems were ever small enough to fit into human memory regardless?

