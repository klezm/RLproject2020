import numpy as np
import random

from Cell import Cell


class Environment:
    def __init__(self, X, Y, isXtorusVar, isYtorusVar, globalActionRewardVar):
        self.grid = np.empty((X,Y), dtype=object)
        self.isTorusVars = (isXtorusVar, isYtorusVar)
        self.globalActionRewardVar = globalActionRewardVar
        self.agentPosition = None

    def update(self, tileData):
        for x in range(self.grid.shape[0]):
            for y in range(self.grid.shape[1]):
                self.grid[x,y] = Cell(**tileData[x,y])

    def give_initial_position(self):
        cellArray = self.grid.flatten()
        candidates = [cell.get_position() for cell in cellArray if cell.isStart]
        if not candidates:  # random start if none is defined
            candidates = [cell.get_position() for cell in cellArray if cell.is_suitable_start()]
        self.agentPosition = random.choice(candidates)
        return self.agentPosition

    def apply_action(self, action):
        destinationEstimate = (self.get_destination_estimate(action, iDim=0),
                               self.get_destination_estimate(action, iDim=1))
        if not self.grid[destinationEstimate].isWall:
            self.agentPosition = destinationEstimate
        reward = self.globalActionRewardVar.get() + self.grid[self.agentPosition].get_arrivalReward()
        episodeFinished = self.grid[self.agentPosition].ends_episode()
        return reward, self.agentPosition, episodeFinished

    def get_destination_estimate(self, action, iDim):
        rawEstimate = self.agentPosition[iDim] + action[iDim]
        dimSize = self.grid.shape[iDim]
        if self.isTorusVars[iDim].get():
            return rawEstimate % dimSize
        else:
            return min(max(rawEstimate, 0), dimSize-1)

    def remove_agent(self):
        self.agentPosition = None
        return self.agentPosition

    def get_grid(self):
        return self.grid
