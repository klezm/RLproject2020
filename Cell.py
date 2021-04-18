class Cell:
    def __init__(self, position, isWall, isStart, isGoal, arrivalReward):
        self.position = position
        self.isWall = isWall
        self.isStart = isStart
        self.isGoal = isGoal
        self.arrivalReward = arrivalReward

    def is_suitable_start(self):
        return not any([self.isWall, self.isGoal])

    def terminates_episode(self):
        return any([self.isGoal])

    def get_position(self):
        return self.position

    def get_arrivalReward(self):
        return self.arrivalReward
