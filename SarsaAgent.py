import numpy as np
import random
from operator import itemgetter

from Agent import Agent


class SarsaAgent(Agent):
    def __init__(self, environment, stepSize, discount, epsilon):
        super().__init__(environment)
        self.stepSize = stepSize
        self.discount = discount
        self.epsilon = epsilon
        self.n = 1
        self.onPolicy = True

    def behavior_policy(self):
        # TODO: Bring this in a form where at most one random number has to be drawn
        if np.random.rand() < self.epsilon:
            #print("Exploratory")
            return random.choice(self.ACTIONS)  # TODO: use np.random
        else:
            return max(self.Qvalues[self.state].items(), key=itemgetter(1))[0]  # TODO: Nondeterministic tiebreaking. So far it doesnt matter since stepsize and discount are usually nonintegers

    def update_actionvalues(self, targetAction):
        if self.memory.get_size() >= self.n:
            actionToUpdate = self.memory.get_action(depth=self.n)
            correspondingState = self.memory.get_state(depth=self.n)
            correspondingReward = self.memory.get_reward(depth=self.n)
            self.Qvalues[correspondingState][actionToUpdate] += self.stepSize * (correspondingReward + self.discount * self.Qvalues[self.state][targetAction] - self.Qvalues[correspondingState][actionToUpdate])
        self.memory.forget_state_action_reward(depth=1)
