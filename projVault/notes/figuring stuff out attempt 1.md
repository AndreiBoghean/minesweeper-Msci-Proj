sooo the december report constitutes..
1. **Title page:** including (in order from top to bottom), your project title, your name in full; and the month and year of submission.
2. **Introduction:** briefly explain the context of the research problem.
3. **Statement of Research Problem:** clearly state the particular problem to be addressed by your project. Explain your motivation and expected contributions for this project.
4. **Literature Survey:** you must complete a thorough review of current research relevant to your project. Critically evaluate the strengths and weaknesses of the work reported in the literature.
5. **Progress:** give a report on your progress thus far, describing the state of your feasibility study, proof of concept, or prototype that demonstrate you are capable of completing your project.
6. **Work Plan:** give an overview of your plan for work for the remainder of the project.
7. **Bibliography:** it is highly recommended that you use a citation manager to generate a high quality list of citations for your report.

the hard parts here are
statement of research problem,
literature survey,
progress,
and work plan.

##### statement of research problem
do we know what our research problem is? no.

why not? all you know is that you want to quantify minesweeper difficulty.
this is just a goal, but why is it a "problem"?
what is the obstacle that would be overcome by the achievement of this goal?
i.e. **what's the problem motivation?**

we can begin by explaining minesweeper,
and explaining the general minesweeper pipeline for a successful game.

that is..
first open a cell.
use your deduction skills to determine neighbouring safe cells.
open the next cell.
repeat.

this process further generalises to..
clear an area as much as is easy to do so.
identify learned minesweeper patterns
apply learned techniques to solve said patterns
continue
^ this process will need a citation to back it up, because it's kinda our core.

the crux of this pipeline is the identification of patterns,
and the application of pattern solutions.

there is a mental cost to pattern identification,
and a processing cost to pattern solving.
if pattern identification fails, the processing cost is wasted.

we want to devise a method of quantification for the processing cost of a pattern,
and ideally also the identification cost of a pattern,
to be able to rank different patterns by their usefulness in a learned pattern arsenal.

ok all that should *justify* and *explain* our **problem** well. (I think).

##### literature survey
we should explore existing attempts at dissecting minesweeper,

and also that funny field about what makes games "fun" rather than mind numbingly complex.
- ^ this is because I think this field will have investigations in correlation between the human gameplay experience, and equivalent computation
  (e.g. I'm hoping to see something like a human finds something challenging if it takes on average 3.6 math operations to solve)

##### progress
our "progress" section here is broken down into 2 parts:
the big picture, with the full unreduced idea you originally planned out
and the reduced version, with just the part about creating the metric.
- ^ important to consider both because the reduced version seems already pretty difficult and by extension the big picture problem is probably unachieavable
###### big picture problem
ok, how can we "prove" that this idea isnt all baloney?
idk lmfao.

to know this idea is feasible, I think I'd want..
1. proof that minesweeper can be broken down into finite subsets of problems
   (similar to that one yt video you watched about sliding shapes...
   adventures in state space by 2swap)
2. and then a way to correlate mental effort to mathematical actions
3. the existance of room for ambiguity in minesweeper solving..
   e.g. there's multiple ways to solve this problem
   or e.g. it's easy to be mistaken about what kind of problem something is

isnt this basically solving the whole problem?
well.. the original plan was applying this mental effort statistic to several patterns,
and then investigating combinations of patterns to find a pattern set that achieves
the best tradeoff between a laziness:time ratio

###### reduced problem
**BUT**..
jess says creating the metric itself is already going to be difficult
==NOTE TO SELF: TODO: CONSIDER REDUCED PROBLEM.==

so.. 
jess phrased it as the finding of the minimum subgraph required to solve a problem
how could we possibly represent a minesweeper problem as a graph?
well, there is a graph of knowledge on the board.
there is a minimum amount of knowledge we need to "unlock" a mine arrangement.
knowledge graphs can be permutations of each other? with more/less complexity
achieving the same outcome

the proper way to do this is using minimum unsatisfiability subgraphs,

##### work plan

