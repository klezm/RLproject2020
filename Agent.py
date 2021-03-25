import numpy as np
import random

from Memory import Memory


class Agent:
    UP = (0,-1)
    DOWN = (0,1)
    LEFT = (-1,0)
    RIGHT = (1,0)
    ACTIONS = [UP, DOWN, LEFT, RIGHT]

    def __init__(self, environment):
        self.environment = environment
        self.onPolicy = True
        self.stepSize = None
        self.discount = None
        self.epsilon = None
        self.memory = Memory()
        self.Qvalues = np.empty_like(self.environment.grid)  # must be kept over episodes
        for x in range(self.Qvalues.shape[0]):
            for y in range(self.Qvalues.shape[1]):
                self.Qvalues[x, y] = {action: self.get_initial_actionvalue() for action in self.ACTIONS}
        self.episodicTask = None  # Todo: This variable is not used so far. Find out if Reward is still a thing in non episodic task, and if, is it defined with or without discount?
        self.episodeFinished = True
        self.state = None
        self.return_ = None
        self.episodeReturns = np.array([])  # must be kept over episodes
        self.lastAction = self.UP  # variable just for demonstration
        self.lastState = None  # variable just for demonstration

    def get_state(self):
        return self.state

    def get_Qvalues(self):
        return self.Qvalues

    def start_episode(self):
        self.episodeFinished = False
        self.return_ = 0  # underscore to avoid naming conflict with return keyword
        self.state = self.environment.give_initial_position()
        if self.state is None:
            print("No Starting Point found")  # TODO: exception

    def step(self):
        #print(self.return_)
        behaviourAction = self.behavior_policy()
        targetAction = behaviourAction if self.onPolicy else self.target_policy()
        self.update_actionvalues(targetAction)
        reward, successorState, self.episodeFinished = self.environment.apply_action(behaviourAction)
        self.return_ += reward
        self.memory.append_state_action_reward((self.state, behaviourAction, reward))
        self.state = successorState
        # TODO: handle last update when episode finished
        if self.episodeFinished:
            self.episodeReturns = np.append(self.episodeReturns, self.return_)
            #print(self.episodeReturns)

    def update_actionvalues(self, reward, successorState):
        self.Qvalues[self.state][self.behaviourAction] += 1

    def target_policy(self):
        pass

    def get_initial_actionvalue(self):
        return 0

    def behavior_policy(self):
        if self.state == self.lastState:
            chosenAction = random.choice(self.ACTIONS)  # TODO: use np.random
        else:
            chosenAction = self.lastAction
        self.lastAction = chosenAction
        self.lastState = self.state
        return chosenAction
