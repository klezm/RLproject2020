# TODO: Plots after run, inspired from the book -> Rewards vs Episode, ... -> mit tkinter aufrufen   A
# TODO: Whole frame in gui to toggle all still hardcoded parameters  L
# TODO: Dynamically change showEveryNsteps and msDelay   L
# TODO: Pause Button   L
# TODO: Epsilon decrease over time, function as argument   A
# TODO: Blink on exploratory move  L
# TODO: Walls in Qvalue / policy maps  L
# TODO: Torus World (can be toggled)  L

# TODO: Finish n-step (MC included)
# TODO: Dynamically change tilesizes w.r.t. grid dimensions on initialize
# TODO: Heatmap background for actionvalues, arrows for greedy policy
#   TODO -> Action-Class, so that for example DOWN = Action(direction: (int, int), color: string, arrow: char)

# TODO: Set agent params by algorithm keyword

# TODO: Entry for some reward number, mousewheel-click on some tile applies that number as arrival reward for that tile
#   TODO -> Remove global arrival reward hardcode
#   TODO -> Find a way to display that i.e. cliff brings back to start AND has a reward of -N (Maybe all "Start Teleporters" in one specific color)

# TODO: Flags for debug stuff and prints, own print function  A

# TODO: Implement planning (Dyna-Q, Dyna-Q+)
# TODO: Dynamically change Gridworld cells
# TODO: Implement Double Learning
# TODO: Implement Expectation-using algorithms
# TODO: King-Moves (can be toggled)
# TODO: (Stochastic) Windy Gridworld (from x & y)
#   TODO -> Action (0,0) as possible action? Show actionvalues in the middle (where greedy policy is now) and greedy policy in some edge
# TODO: Teleporters
# TODO: Ice Floor (can be toggled) -> Hard to solve for human, but no extra challenge for RL Agent!
# TODO: Value-Based TD
# TODO: Implement Policy Evaluation, Policy Improvement, Policy Iteration, Value Iteration