class Cell:
    def __init__(self, position, isWall, isStart, isGoal, arrivalRewardVar):
        self.position = position
        self.isWall = isWall
        self.isStart = isStart
        self.isGoal = isGoal
        self.arrivalRewardVar = arrivalRewardVar

    def is_suitable_start(self):  # TODO: Anpassen für Teleporter
        return not any([self.isWall, self.isGoal])

    def terminates_episode(self):
        return any([self.isGoal])

    def get_position(self):
        return self.position

    def get_arrivalReward(self):
        return self.arrivalRewardVar.get()
