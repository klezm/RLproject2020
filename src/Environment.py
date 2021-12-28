import numpy as np
import random

from myFuncs import matrix, hRange, wRange, evaluate, shape
from Cell import Cell


class Environment:
    """Holds all data about the gridworld environment an agent interacts with and defines its behaviour.
     ..
    Supported features include (non-)episodic tasks, applying changes between episodes,
    customizable cell rewards, randomized start, (randomizable) teleporters, wind,
    cylinder- and torus-shaped maps, and an icy floor.\n
    This features may be combined mostly without restrictions and allow
    rebuilding most of the gridworlds introduced in the book
    "Reinforcement Learning - An Introduction" by Sutton & Barto.
    """
    def __init__(self, H, W, hasIceFloorVar, isHtorusVar, isWtorusVar, hWindVars, wWindVars):
        self.grid = matrix(H, W)
        self.hasIceFloorVar = hasIceFloorVar
        self.isTorusVars = (isHtorusVar, isWtorusVar)
        self.windVars = (hWindVars, wWindVars)
        self.agentPosition = None  # In a gridworld, position and agent state can be treated equivalent, but not in general! i.e. snake
        self.teleportJustUsed = None  # needed as a flag for coloring this tile yellow
        self.windJustUsed = None

    def update(self, tileData):
        for h in hRange(self.grid):
            for w in wRange(self.grid):
                self.grid[h][w] = Cell(**tileData[h][w])

    def apply_action(self, action):
        # Step, Wind & Ice:
        self.windJustUsed = None
        oldEstimate = self.agentPosition
        while True:
            stepDestinationEstimate = self._get_step_destination(oldEstimate, action)  # processes world edge / torus / wall
            windDestinationEstimate = self._get_wind_destination(stepDestinationEstimate)
            if windDestinationEstimate != stepDestinationEstimate:
                self.windJustUsed = stepDestinationEstimate
            if not self.hasIceFloorVar.get() or windDestinationEstimate == oldEstimate:
                break
            oldEstimate = windDestinationEstimate
        self.agentPosition = windDestinationEstimate
        reward = self._gather_reward()
        # Teleporter:
        self.teleportJustUsed = None
        if evaluate(self.grid, self.agentPosition).is_teleport_entry():
            self.teleportJustUsed = self.agentPosition  # needed for coloring
            self.agentPosition = self._get_teleport_destination(self.agentPosition)
            reward += self._gather_reward()
        # Goal:
        episodeFinished = evaluate(self.grid, self.agentPosition).terminates_episode()
        return reward, self.agentPosition, episodeFinished

    def give_initial_position(self):
        cellArray = np.array(self.grid).flatten()
        candidates = [cell.get_position() for cell in cellArray if cell.isStart]
        if not candidates:  # random start if none is defined
            candidates = [cell.get_position() for cell in cellArray if cell.is_suitable_spawn()]
        if not candidates:
            candidates = [None]
        self.agentPosition = random.choice(candidates)
        return self.agentPosition

    def remove_agent(self):
        self.agentPosition = None
        return self.agentPosition

    def _get_teleport_destination(self, position):
        entryCell = evaluate(self.grid, position)
        teleportName = entryCell.teleportSink
        cellArray = np.array(self.grid).flatten()
        candidates = [cell.get_position() for cell in cellArray if (cell.is_teleportName_destination(teleportName) and cell is not entryCell)]
        if not candidates:  # random destination if no free source of this teleporter is available
            candidates = [cell.get_position() for cell in cellArray if (cell.is_suitable_spawn())]
        if not candidates:
            candidates = [position]
        return random.choice(candidates)

    def _get_step_destination(self, position, step):
        estimate = [-1, -1]
        for iDim in [0,1]:
            rawEstimate = position[iDim] + step[iDim]
            dimSize = shape(self.grid)[iDim]
            if self.isTorusVars[iDim].get():
                estimate[iDim] = rawEstimate % dimSize
            else:
                estimate[iDim] = min(max(rawEstimate, 0), dimSize-1)
        estimate = tuple(estimate)
        if evaluate(self.grid, estimate).isWall:
            return position
        return estimate

    def _get_wind_destination(self, position):
        wind = [self.windVars[0][position[1]].get(),
                self.windVars[1][position[0]].get()]
        absWind = np.abs(wind)
        if any(wind) and (0 in wind or absWind[0] == absWind[1]):   # only apply wind if one wind dim is zero or both are equally nonzero strong
            maxWindStrength = np.max(absWind)
            windDirection = np.sign(wind)
            for i in range(maxWindStrength):
                afterWindEstimate = self._get_step_destination(position=position, step=windDirection)
                if afterWindEstimate == position:  # no more movement
                    break
                position = afterWindEstimate
        return position

    def _gather_reward(self):
        return evaluate(self.grid, self.agentPosition).get_arrivalReward()

    def get_grid(self):
        return self.grid

    def get_teleportJustUsed(self):
        return self.teleportJustUsed

    def get_windJustUsed(self):
        return self.windJustUsed
