import random


class Policy:
    def __init__(self, agent):
        self.agent = agent

    def give_greedy_action(self, state):
        greedyActions = self.agent.get_greedyActions()[state]
        if len(greedyActions) == 1:  # only use rng if necessary
            return greedyActions[0]
        else:
            return random.choice(greedyActions)
        
    def sample_random_action(self):
        return random.choice(self.agent.ACTIONSPACE)
        # We can use this one-liner ONLY BECAUSE in a gridworld, the actionspace does not depend on the state.
    
    def generate_action(self, state):
        return None
    
    def get_expected_actionvalue(self, state):
        return None
