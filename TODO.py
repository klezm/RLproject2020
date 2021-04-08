# TODO: epsilon decay per step and per episode
# TODO: Policy as class for expectation algorithms
# TODO: Proper flow control
# TODO: Implement Expectation-using algorithms
# TODO: Implement Double Learning
# TODO: Implement planning (Dyna-Q, Dyna-Q+)
#   TODO -> Dynamically change Gridworld cells
#   TODO -> check and rework wall/start/goal appearances in visualization maps once dynamic environment changing is gonna be implemented
#   TODO -> Load/Save maps/dict:{timestep: map} from/in file
# TODO: Entry for some reward number, mousewheel-click on some tile applies that number as arrival reward for that tile
#   TODO -> Find a way to display that i.e. cliff brings back to start AND has a reward of -N (Maybe all "Start Teleporters" in one specific color)

# TODO: Heatmap background for actionvalues (In action-color) for changes
# TODO: Visualize Agent Trace (The longer a tile was not visited, the more the trace on that tile fades)
# TODO: (Stochastic) Windy Gridworld (from x & y)
#   TODO -> Action (0,0) as possible action? Show actionvalues in the middle (where greedy policy is now) and greedy policy in some edge
# TODO: King-Moves (can be toggled)
# TODO: Teleporters
# TODO: Ice Floor (can be toggled) -> Hard to solve for human, but no extra challenge for RL Agent!
# TODO: independent epsilons for behaviour and target policy
# TODO: fonts not hardcoded
# TODO: initial actionvalue mean and sigma in gui
# TODO: Handle n-step off-policy by either disabling off-policy if n>1 or by introducing that rho factor
# TODO: Set agent params by algorithm keyword
# TODO: Plot Reward vs Timestep for non-episodic Tasks
# TODO: Dynamically change tilesizes w.r.t. grid dimensions on initialize
# TODO: Flags for debug stuff and prints, own print function

# TODO: Implement Statevalue-Based TD
# TODO: Implement Policy Evaluation, Policy Improvement, Policy Iteration, Value Iteration
