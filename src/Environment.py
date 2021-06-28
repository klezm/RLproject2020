import numpy as np
import random

from Cell import Cell


class Environment:
    def __init__(self, X, Y, hasIceFloorVar, isXtorusVar, isYtorusVar, xWindVars, yWindVars):
        self.grid = np.empty((X,Y), dtype=Cell)
        self.hasIceFloorVar = hasIceFloorVar
        self.isTorusVars = (isXtorusVar, isYtorusVar)
        self.windVars = (xWindVars, yWindVars)
        self.agentPosition = None  # In a gridworld, position and agent state can be treated equivalent, but not in general! i.e. snake
        self.teleportJustUsed = None  # needed as a flag for coloring this tile yellow


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
        oldEstimate = self.agentPosition
        while True:
            destinationEstimate = self.get_step_destination(oldEstimate, action)  # processes world edge / torus / wall
            destinationEstimate = self.get_wind_destination(destinationEstimate)
            if not self.hasIceFloorVar.get() or destinationEstimate == oldEstimate:
                break
            oldEstimate = destinationEstimate
        self.agentPosition = destinationEstimate
        reward = self.gather_reward()
        if self.grid[self.agentPosition].is_teleport_entry():
            self.teleportJustUsed = self.agentPosition
            self.agentPosition = self.get_teleport_destination(self.grid[self.agentPosition])
            reward += self.gather_reward()
        else:
            self.teleportJustUsed = None
        episodeFinished = self.grid[self.agentPosition].terminates_episode()
        return reward, self.agentPosition, episodeFinished

    def get_step_destination(self, position, step):
        estimate = [-1, -1]
        for iDim in [0,1]:
            rawEstimate = position[iDim] + step[iDim]
            dimSize = self.grid.shape[iDim]
            if self.isTorusVars[iDim].get():
                estimate[iDim] = rawEstimate % dimSize
            else:
                estimate[iDim] = min(max(rawEstimate, 0), dimSize-1)
        estimate = tuple(estimate)
        if self.grid[estimate].isWall:
            return position
        return estimate

    def get_wind_destination(self, position):
        wind = [0,0]
        for iDim in [0,1]:
            wind[iDim] = self.windVars[iDim][position[not iDim]].get()
        absWind = np.abs(wind)
        if any(wind) and (0 in wind or absWind[0] == absWind[1]):   # only apply wind if one wind dim is zero or both are equally nonzero strong
            maxWindStrength = np.max(absWind)
            windDirection = np.sign(wind)
            for i in range(maxWindStrength):
                afterWindEstimate = self.get_step_destination(position=position, step=windDirection)
                if afterWindEstimate == position:  # no more movement
                    break
                position = afterWindEstimate
        return position

    def gather_reward(self):
        return self.grid[self.agentPosition].get_arrivalReward()

    def remove_agent(self):
        self.agentPosition = None
        return self.agentPosition

    def get_grid(self):
        return self.grid

    def get_teleportJustUsed(self):
        return self.teleportJustUsed
