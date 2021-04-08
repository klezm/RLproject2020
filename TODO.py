# TODO: Blink on exploratory still correct?
# TODO: epsilon decay per step and per episode
# TODO: MC Learning Rate 1/count(S,A)

# TODO: Plots after run, inspired from the book -> Rewards vs Episode, ... -> mit tkinter aufrufen   A
# TODO: Plot Reward vs Timestep for non-episodic Tasks!
# TODO: Pause Button   L
# TODO: Heatmap background for actionvalues (In action-color!)  L Not helpful...
# TODO: Improve step function  L  Nothing to improve.
# TODO: Torus World (can be toggled for x or y or both)  L
# TODO: Presentation: Mainly just running the program and explaining, program structure, outlook slides in the end. Convergence comparison Qlearning and constant-epsilon-Sarsa. On the fly created plots.


# TODO: Finish n-step (MC included)
# TODO: Dynamically change tilesizes w.r.t. grid dimensions on initialize

# TODO: Set agent params by algorithm keyword

# TODO: Entry for some reward number, mousewheel-click on some tile applies that number as arrival reward for that tile
#   TODO -> Find a way to display that i.e. cliff brings back to start AND has a reward of -N (Maybe all "Start Teleporters" in one specific color)

# TODO: Flags for debug stuff and prints, own print function  A

# TODO: Implement planning (Dyna-Q, Dyna-Q+)
#   TODO -> Dynamically change Gridworld cells
#   TODO -> check and rework wall/start/goal appearances in visualization maps once dynamic environment changing is gonna be implemented
# TODO: Implement Double Learning
# TODO: Implement Expectation-using algorithms
# TODO: King-Moves (can be toggled)
# TODO: (Stochastic) Windy Gridworld (from x & y)
#   TODO -> Action (0,0) as possible action? Show actionvalues in the middle (where greedy policy is now) and greedy policy in some edge
# TODO: Teleporters
# TODO: Ice Floor (can be toggled) -> Hard to solve for human, but no extra challenge for RL Agent!
# TODO: Value-Based TD
# TODO: Implement Policy Evaluation, Policy Improvement, Policy Iteration, Value Iteration
# TODO: wrapper für tkVar getter damit man nicht mehr casten muss -> setter überschrieben für nachkommastellen
# TODO: fonts not hardcoded
# TODO: independent epsilons for behaviour and target policy
# TODO: initial actionvalue mean and sigma in gui
# TODO: Load/Save maps from/in file
# TODO: Change empty Entryfields to 0/1 (not needed when interaction only possible between episodes)
# TODO: Handle n-step off-policy by either disabliing off-policy if n>1 or by introducing that rho factor