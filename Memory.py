from collections import deque

from myFuncs import cached_power


class Memory:
    def __init__(self, agent):
        self.agent = agent
        self.memory = deque()  # most efficient for appending and popping from both sides
        self.discountedRewardSum = 0

    def memorize(self, state, action, reward):
        self.memory.appendleft((state, action, reward))  # the higher the index, the older the memory
        self.discountedRewardSum *= self.agent.get_discount()
        self.discountedRewardSum += reward

    def get_oldest_memory(self):
        return self.memory[-1]

    def forget_oldest_memory(self):
        _, _, reward = self.memory.pop()
        self.discountedRewardSum -= cached_power(self.agent.get_discount(), self.get_size()) * reward  # get_size() here returns the original size minus one

    def get_discountedRewardSum(self):
        return self.discountedRewardSum

    def get_size(self):
        return len(self.memory)
