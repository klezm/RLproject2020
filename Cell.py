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
