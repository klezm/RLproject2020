import numpy as np
import random
from operator import itemgetter

from Agent import Agent


class SarsaAgent(Agent):
    def __init__(self, environment, stepSize, discount, epsilon, actionPlan=[]):
        super().__init__(environment, actionPlan)
        self.stepSize = stepSize
        self.discount = discount
        self.epsilon = epsilon
        self.n = 1
        self.onPolicy = True

    def behavior_policy(self):
        if self.actionPlan:
            return self.actionPlan.pop(0)
        # TODO: Bring this in a form where at most one random number has to be drawn
        if np.random.rand() < self.epsilon:
            #print("Exploratory")
            actionCandidates = self.ACTIONS
        else:  # greedy
            maxActionValue = max(self.Qvalues[self.state].values())
            actionCandidates = [action for action, value in self.Qvalues[self.state].items() if value == maxActionValue]
        if len(actionCandidates) > 1:
            return random.choice(actionCandidates)  # TODO: use np.random
        else:  # dunno if random.choice is optimized so that it doesnt use a rng if container size is 1
            return actionCandidates[0]

    def target_policy(self):
        maxActionValue = max(self.Qvalues[self.state].values())
        actionCandidates = [action for action, value in self.Qvalues[self.state].items() if value == maxActionValue]
        if len(actionCandidates) > 1:
            return random.choice(actionCandidates)  # TODO: use np.random
        else:  # dunno if random.choice is optimized so that it doesnt use a rng if container size is 1
            return actionCandidates[0]

    def update_actionvalues(self, targetActionValue):
        if self.memory.get_size() >= self.n:
            actionToUpdate = self.memory.get_action(depth=self.n)
            correspondingState = self.memory.get_state(depth=self.n)
            correspondingReward = self.memory.get_reward(depth=self.n)  # Below: part after += in extra line
            Qbefore = self.Q(S=correspondingState, A=actionToUpdate)
            error = correspondingReward + self.discount * targetActionValue - Qbefore
            update = self.stepSize * error
            Qafter = Qbefore + update
            self.Qvalues[correspondingState][actionToUpdate] = Qafter
            self.memory.forget_state_action_reward(depth=1)
