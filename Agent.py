import numpy as np


class Agent:
    UP = (-1,0)
    DOWN = (1,0)
    LEFT = (0,-1)
    RIGHT = (0,1)
    ACTIONS = [UP, DOWN, LEFT, RIGHT]

    def __init__(self, environment, sizeGuess=100):
        self.environment = environment
        self.Qvalues = np.empty((sizeGuess, sizeGuess), dtype=np.object)
        self.state = None

    def ready(self):
        for x in range(self.Qvalues.shape[0]):
            for y in range(self.Qvalues.shape[1]):
                self.Qvalues[x,y] = {action: self.get_initial_actionvalue() for action in self.ACTIONS}
        self.state = self.environment.give_initial_position()
        if self.state is None:
            print("No Starting Point found")  # TODO: exception


    def step(self):
        action = self.choose_action()
        reward, successorState = self.environment.apply_action(action)
        print(f"State:{state}\tReward:{reward}\tSuccessor State:{successorState}")
        self.state = successorState

    def get_initial_actionvalue(self):
        return 0

    def choose_action(self):
        return self.UP
