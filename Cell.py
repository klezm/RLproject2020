import numpy as np


class Cell:
    def __init__(self, position, isWall, isStart, isGoal, arrivalReward):
        self.position = position
        self.isWall = isWall
        self.isStart = isStart
        self.isGoal = isGoal
        self.arrivalReward = arrivalReward

    def get_position(self):
        return self.position

    def get_arrival_reward(self):
        return self.arrivalReward

    def is_suitable_start(self):
        return not any([self.isWall, self.isGoal])

    def ends_episode(self):
        return any([self.isGoal])
