class Cell:
    def __init__(self, position, isWall, isStart, isGoal, arrivalRewardVar, teleportSource, teleportSink):
        self.position = position
        self.isWall = isWall
        self.isStart = isStart
        self.isGoal = isGoal
        self.arrivalRewardVar = arrivalRewardVar
        self.teleportSource = teleportSource
        self.teleportSink = teleportSink

    def is_suitable_spawn(self):
        return not any([self.isWall, self.isGoal, self.is_teleport_entry()])

    def terminates_episode(self):
        return any([self.isGoal])

    def get_position(self):
        return self.position

    def get_arrivalReward(self):
        return self.arrivalRewardVar.get()

    def is_teleportName_destination(self, name):
        return self.teleportSource == name

    def is_teleport_entry(self):
        return bool(self.teleportSink)
