from collections import deque

from myFuncs import cached_power


class Memory:
    def __init__(self, agent):
        self.agent = agent
        self.memory = deque()
        self.discountedRewardSum = 0

    def memorize(self, state, action, reward):
        self.memory.appendleft((state, action, reward))
        self.discountedRewardSum *= self.agent.get_discount()
        self.discountedRewardSum += reward

    def pop_oldest_state_action(self):
        state, action, reward = self.memory.pop()
        self.discountedRewardSum -= cached_power(self.agent.get_discount(), self.get_size()) * reward  # Because of pop, get_size() is always nStep-1 if memory was "full"
        return action, state

    def get_discountedRewardSum(self):
        return self.discountedRewardSum

    def get_size(self):
        return len(self.memory)

