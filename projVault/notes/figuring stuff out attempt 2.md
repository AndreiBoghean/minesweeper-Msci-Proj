to measure minesweeper area difficulty:
- need an objectively correct measure.
..that means you NEED human data :(

the crux of the project is to fit a constraint programming model to the behaviour of a human, as per that sokoban paper

##### data collection
do we want to do this? I think **not** because.. *problem*:
manual fitting would operate solely on time spent.. 
and there is no way to measure the mental strain of the human.
what indication is there whether the 30 seconds of human inaction is because they're doing hard math, or because they're just counting a pattern?

*solution*? what if we query for whether the field is either boring or challenging?
if a field takes a long amount of time, but it was marked boring, that suggests it has a lot of simple but cumbersome moves.
if a field takes a long amount of time, but it was marked challenging, that's what we expect... etc.

|            | boring?        | challenging? |
| ---------- | -------------- | ------------ |
| long time  | **monotonous** | **hard**     |
| short time | *easy*         | **complex**  |

with these cases, we'd expect humans to demonstrate an advantage in short easy tasks,
with machines excelling everywhere else.

##### data fitting

the sokoban paper suggests there is some other factor involved in the tradeoff between human and machine skill,
because humans are exceedingly good at some specific simple puzzles.
^ to investigate this, maybe we'd want to find a way to investigate ==pspace== stuff?

the paper's model evaluates tradeoffs between *neighbouring states* and the *current state*.
it scores each state according to it's distance from the end goal,
but adds a **constant coefficiant** to bias a state if that state has a *smaller distance than the current state*.
it then selects a state randomly, with each state's probability correlating to it's score.

as a possible state's distance decreases, the coefficient is naturally larger in it's score
which biases the model to be more "correct" when it's closer to the solution.


##### footnotes:
useful sokoban site: https://sokoban-max-moves.herokuapp.com/build