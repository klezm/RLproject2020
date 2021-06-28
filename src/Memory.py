from collections import deque

from myFuncs import cached_power


class Memory(deque):
    def __init__(self, agent):
        super().__init__()
        self.agent = agent
        self.discountedRewardSum = 0
        self.lastForgottenState = None

    def memorize(self, state, action, reward):
        self.appendleft((state, action, reward))  # the higher the index, the older the memory
        self.discountedRewardSum *= self.agent.get_discount()
        self.discountedRewardSum += reward

    def get_oldest_memory(self):
        return self[-1]

    def forget_oldest_memory(self):
        self.lastForgottenState, _, reward = self.pop()
        self.discountedRewardSum -= cached_power(self.agent.get_discount(), len(self)) * reward  # len(self) here returns the original size minus one, because of the pop

    def yield_lastForgottenState(self):  # needed for trace visualization
        state = self.lastForgottenState
        self.lastForgottenState = None
        return state

    def get_discountedRewardSum(self):
        return self.discountedRewardSum
