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
        self.position = self.give_initial_position()

    def give_initial_position(self):
        candidates = [cell.position for cell in self.grid.flatten() if cell.isStart]
        if candidates:
            return random.choice(candidates)
        else:
            return None

    def apply_action(self, action):
        reward = self.globalActionReward
        xEstimate = self.position[0] + action[0]
        yEstimate = self.position[1] + action[1]
        if 0 <= xEstimate < self.X and 0 <= yEstimate < self.Y and not self.grid[xEstimate, yEstimate].isWall:
            self.position = (xEstimate, yEstimate)
            reward += self.grid[self.position].arrivalReward
        return reward, self.position
