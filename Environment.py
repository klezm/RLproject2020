import numpy as np
import random

from Cell import Cell


class Environment:
    def __init__(self, X, Y, hasIceFloorVar, isXtorusVar, isYtorusVar):
        self.grid = np.empty((X,Y), dtype=Cell)
        self.hasIceFloorVar = hasIceFloorVar
        self.isTorusVars = (isXtorusVar, isYtorusVar)
        self.agentPosition = None
        self.teleportJustUsed = None
        # In a gridworld, position and agent state can be treated equivalent, but not in general! i.e. snake

    def update(self, tileData):
        for x in range(self.grid.shape[0]):
            for y in range(self.grid.shape[1]):
                self.grid[x,y] = Cell(**tileData[x,y])

    def give_initial_position(self):
        cellArray = self.grid.flatten()
        candidates = [cell.get_position() for cell in cellArray if cell.isStart]
        if not candidates:  # random start if none is defined
            candidates = [cell.get_position() for cell in cellArray if cell.is_suitable_spawn()]
        if not candidates:
            candidates = [None]
        self.agentPosition = random.choice(candidates)
        return self.agentPosition

    def get_teleport_destination(self, entryCell):
        teleportName = entryCell.teleportSink
        cellArray = self.grid.flatten()
        candidates = [cell.get_position() for cell in cellArray if (cell.is_teleportName_destination(teleportName) and cell is not entryCell)]
        if not candidates:  # random destination if no free source of this teleporter is available
            candidates = [cell.get_position() for cell in cellArray if (cell.is_suitable_spawn())]
        if not candidates:
            candidates = [entryCell.get_position()]
        return random.choice(candidates)

    def apply_action(self, action):
        while True:
            destinationEstimate = self.get_destination_estimate(self.agentPosition, action)
            if self.grid[destinationEstimate].isWall or destinationEstimate == self.agentPosition:
                break
            self.agentPosition = destinationEstimate
            if not self.hasIceFloorVar.get():
                break
        reward = self.grid[self.agentPosition].get_arrivalReward()
        if self.grid[self.agentPosition].is_teleport_entry():
            self.teleportJustUsed = self.agentPosition
            self.agentPosition = self.get_teleport_destination(self.grid[self.agentPosition])
            reward += self.grid[self.agentPosition].get_arrivalReward()
        else:
            self.teleportJustUsed = None
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

    def get_teleportJustUsed(self):
        return self.teleportJustUsed
