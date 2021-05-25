import numpy as np
import random

from Cell import Cell


class Environment:
    def __init__(self, X, Y, hasIceFloorVar, isXtorusVar, isYtorusVar):
        self.grid = np.empty((X,Y), dtype=Cell)
        self.hasIceFloorVar = hasIceFloorVar
        self.isTorusVars = (isXtorusVar, isYtorusVar)
        self.agentPosition = None
        # In a gridworld, position and agent state can be treated equivalent, but not in general! i.e. snake

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
        oldPosition = self.agentPosition
        while True:
            destinationEstimate = self.get_destination_estimate(oldPosition, action)
            if self.grid[destinationEstimate].isWall or destinationEstimate == oldPosition:
                # last case: agent hit world edge
                self.agentPosition = oldPosition
                break
            elif self.hasIceFloorVar.get():
                oldPosition = destinationEstimate
            else:
                self.agentPosition = destinationEstimate
                break
        reward = self.grid[self.agentPosition].get_arrivalReward()
        episodeFinished = self.grid[self.agentPosition].terminates_episode()
        return reward, self.agentPosition, episodeFinished

    def get_destination_estimate(self, position, action):
        estimate = [-1, -1]
        for iDim in range(2):
            rawEstimate = position[iDim] + action[iDim]
            dimSize = self.grid.shape[iDim]
            if self.isTorusVars[iDim].get():
                estimate[iDim] = rawEstimate % dimSize
            else:
                estimate[iDim] = min(max(rawEstimate, 0), dimSize-1)
        return tuple(estimate)

    def remove_agent(self):
        self.agentPosition = None
        return self.agentPosition

    def get_grid(self):
        return self.grid
