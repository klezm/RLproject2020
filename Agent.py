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
        self.Qvalues = np.empty_like(self.environment.grid)  # must be kept over episodes
        for x in range(self.Qvalues.shape[0]):
            for y in range(self.Qvalues.shape[1]):
                self.Qvalues[x, y] = {action: self.get_initial_actionvalue() for action in self.ACTIONS}
        self.episodeFinished = True
        self.state = None
        self.return_ = None
        self.episodeReturns = np.array([])  # must be kept over episodes
        self.lastAction = self.UP  # variable just for demonstration
        self.lastState = None  # variable just for demonstration

    def start_episode(self):
        self.episodeFinished = False
        self.return_ = 0  # underscore to avoid naming conflict with return keyword
        self.state = self.environment.give_initial_position()
        if self.state is None:
            print("No Starting Point found")  # TODO: exception

    def step(self):
        action = self.choose_action()
        reward, successorState, self.episodeFinished = self.environment.apply_action(action)
        #print(f"State:{self.state}\tReward:{reward}\tSuccessor State:{successorState}")
        self.Qvalues[self.state][action] += 1
        #print(self.Qvalues)
        self.state = successorState
        self.return_ += reward
        if self.episodeFinished:
            self.episodeReturns = np.append(self.episodeReturns, self.return_)
            #print(self.episodeReturns)

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
