import random

from myFuncs import evaluate


class Policy:
    """Base Class for policies used by an ``Agent``.
    A policy object may be set as his behaviour- or his target policy.\n
    A policy may decide greedy actions, sample random actions and calculate
    expected actionvalues, based on the value tables provided by the ``Agent``.
    """
    def __init__(self, agent):
        self.agent = agent

    def give_greedy_action(self, state):
        greedyActions = evaluate(self.agent.get_greedyActions(), state)
        if len(greedyActions) == 1:  # use rng only if necessary
            return greedyActions[0]
        else:
            return random.choice(greedyActions)
        
    def sample_random_action(self):
        return random.choice(self.agent.get_actionspace())
        # We can use this one-liner ONLY BECAUSE in a gridworld, the actionspace does not depend on the state.
    
    def generate_action(self, state):
        """Should be overwritten by daughter classes.
        """
        pass

    def get_expected_actionvalue(self, state):
        """Should be overwritten by daughter classes.
        """
        pass
