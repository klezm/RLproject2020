import numpy as np
import random

from Cell import Cell


class Environment:
    def __init__(self, data):
        tileData = data["tileData"]
        self.grid = np.empty_like(tileData)
        for x in range(self.grid.shape[0]):
            for y in range(self.grid.shape[1]):
                self.grid[x,y] = Cell(**tileData[x,y])
        self.globalActionReward = data["globalActionReward"]
        self.isTorus = (data["isXtorus"], data["isYtorus"])
        self.agentPosition = None

    def give_initial_position(self):
        cellArray = self.grid.flatten()
        candidates = [cell.get_position() for cell in cellArray if cell.isStart]
        if not candidates:  # random start is none is defined
            candidates = [cell.get_position() for cell in cellArray if cell.is_suitable_start()]
        self.agentPosition = random.choice(candidates)  # TODO: use np.random
        return self.agentPosition

    def apply_action(self, action):
        destinationEstimate = (self.get_destination_estimate(action, iDim=0),
                               self.get_destination_estimate(action, iDim=1))
        if not self.grid[destinationEstimate].isWall:
            self.agentPosition = destinationEstimate
        reward = self.globalActionReward.get() + self.grid[self.agentPosition].get_arrival_reward()
        episodeFinished = self.grid[self.agentPosition].ends_episode()
        return reward, self.agentPosition, episodeFinished

    def get_destination_estimate(self, action, iDim):
        rawEstimate = self.agentPosition[iDim] + action[iDim]
        dimSize = self.grid.shape[iDim]
        if self.isTorus[iDim].get():
            return rawEstimate % dimSize
        else:
            return min(max(rawEstimate, 0), dimSize-1)
