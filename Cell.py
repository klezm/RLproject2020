class Cell:
    def __init__(self, position, isWall, isStart, isGoal, arrivalReward):
        self.position = position
        self.isWall = isWall
        self.isStart = isStart
        self.isGoal = isGoal
        self.arrivalReward = arrivalReward
