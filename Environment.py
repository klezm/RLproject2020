import numpy as np
import random

from Cell import Cell


class Environment:
    def __init__(self, data):
        envData = data["environmentData"]
        self.grid = np.empty_like(envData)
        self.X, self.Y = self.grid.shape
        for x in range(self.X):
            for y in range(self.Y):
                self.grid[x,y] = Cell(**envData[x,y])
        self.globalActionReward = data["globalActionReward"]
        self.agentPosition = None

    def give_initial_position(self):
        candidates = [cell.get_position() for cell in self.grid.flatten() if cell.isStart]
        if candidates:
            self.agentPosition = random.choice(candidates)  # TODO: use np.random
        else:
            self.agentPosition = None
        return self.agentPosition

    def apply_action(self, action):
        episodeFinished = False
        reward = self.globalActionReward
        xEstimate = self.agentPosition[0] + action[0]
        yEstimate = self.agentPosition[1] + action[1]
        if 0 <= xEstimate < self.X and 0 <= yEstimate < self.Y and not self.grid[xEstimate, yEstimate].isWall:
            self.agentPosition = (xEstimate, yEstimate)
            reward += self.grid[self.agentPosition].get_arrival_reward()
            episodeFinished = self.grid[self.agentPosition].isGoal
        return reward, self.agentPosition, episodeFinished
