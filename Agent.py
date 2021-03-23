import numpy as np
import random

class Agent:
    UP = (0,-1)
    DOWN = (0,1)
    LEFT = (-1,0)
    RIGHT = (1,0)
    ACTIONS = [UP, DOWN, LEFT, RIGHT]

    def __init__(self, environment, sizeGuess=100):
        self.environment = environment
        self.Qvalues = np.empty((sizeGuess, sizeGuess), dtype=np.object)
        self.state = None
        self.lastAction = self.UP  # variable just for demonstration
        self.lastState = None  # variable just for demonstration

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
        print(f"State:{self.state}\tReward:{reward}\tSuccessor State:{successorState}")
        self.state = successorState

    def get_initial_actionvalue(self):
        return 0

    def choose_action(self):
        if self.state == self.lastState:
            chosenAction = random.choice(self.ACTIONS)
        else:
            chosenAction = self.lastAction
        self.lastAction = chosenAction
        self.lastState = self.state
        return chosenAction
