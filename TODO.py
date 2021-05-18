# TODO: remove cycle maps feature
# TODO: check (and improve) tile_policy_types def and usage, rework Tile.py
#   TODO -> Try to easily include King-Moves
# TODO: rename pargs keys consistently / Better: Read from easy editable yaml config -> adjust readme
# TODO: "if True:"-Einrückungen in GUI init für übersicht
# TODO: Free bottlenecks from np object arrays
# TODO: Add remaining argtypes
# TODO: Implement planning (Dyna-Q, Dyna-Q+)
#   TODO -> Load/Save maps/dict:{timestep: map} from/in file
# TODO: Entry for some reward number, mousewheel-click on some tile applies that number as arrival reward for that tile
#   TODO -> Find a way to display that i.e. cliff brings back to start AND has a reward of -N (Maybe all "Start Teleporters" in one specific color)
# TODO: Flag: "Decay Epsilon Episode-wise"
# TODO: Plot all parameters vs timestep -> Give the paramframes names as identifier, then put them into a dict with key equal to name, makes  plotting of params in the end easier
# TODO: Implement Double Learning

# TODO: Use property instead of getter/setter
# TODO: Visualize Agent Trace (The longer a tile was not visited, the more the trace on that tile fades) (intensity = (1 - (min(nstep, i_steps_unvisited) / nstep) * 255
# TODO: (Stochastic) Windy Gridworld (from x & y)
#   TODO -> Action (0,0) as possible action? Show actionvalues in the middle (where greedy policy is now) and greedy policy in some edge
# TODO: King-Moves (can be toggled)
# TODO: Teleporters
# TODO: Ice Floor (can be toggled) -> Hard to solve for human, but no extra challenge for RL Agent!
# TODO: fonts not hardcoded
# TODO: initial actionvalue mean and sigma in gui
# TODO: Set agent params by algorithm keyword
# TODO: Plot Reward vs Timestep for non-episodic Tasks
# TODO: Allow running n Agents one after another with fixed params and without visualization to make average plots
#   TODO -> Nice once {timestep: map} is implemented
# TODO: Dynamically change tilesizes w.r.t. grid dimensions on initialize
# TODO: Flags for debug stuff and prints, own print function
# TODO: Yaml config instead of pseudoconstant statics

# TODO: Implement Statevalue-Based TD
# TODO: Implement Policy Evaluation, Policy Improvement, Policy Iteration, Value Iteration
