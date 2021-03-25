import numpy as np
import random

from Memory import Memory


class Agent:
    UP = (0,-1)
    DOWN = (0,1)
    LEFT = (-1,0)
    RIGHT = (1,0)
    ACTIONS = [UP, DOWN, LEFT, RIGHT]

    def __init__(self, environment, actionPlan=[]):
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
        self.actionPlan = actionPlan
        self.actionHistory = []

    def get_state(self):
        return self.state

    def get_Qvalues(self):
        return self.Qvalues

    def Q(self, S, A):
        return self.Qvalues[S][A]

    #def get_action_value_from_policy(self, policy):
    #    action = policy()
    #    actionValue = self.Q(self.state, action)
    #    return action, actionValue

    def start_episode(self):
        self.episodeFinished = False
        self.return_ = 0  # underscore to avoid naming conflict with return keyword
        self.state = self.environment.give_initial_position()
        if self.state is None:
            print("No Starting Point found")  # TODO: exception

    def step(self):
        #print(self.return_)
        behaviorAction = self.behavior_policy()
        if self.onPolicy:
            targetAction = behaviorAction
        else:
            targetAction = self.target_policy()
        targetActionValue = self.Q(S=self.state, A=targetAction)
        self.update_actionvalues(targetActionValue)
        reward, successorState, self.episodeFinished = self.environment.apply_action(behaviorAction)
        self.actionHistory.append(behaviorAction)
        #print(self.actionHistory)
        self.return_ += reward
        self.memory.memorize_state_action_reward((self.state, behaviorAction, reward))
        self.state = successorState

    def process_remaining_memory(self):
        self.episodeReturns = np.append(self.episodeReturns, self.return_)
        while self.memory.get_size():
            self.update_actionvalues(targetActionValue=0)


    def update_actionvalues(self, reward, successorState):
        # Just some dummy non-RL update rule
        self.Qvalues[self.state][self.behaviourAction] += 1

    def target_policy(self):
        pass

    def get_initial_actionvalue(self):
        return 0

    def behavior_policy(self):
        # Just some dummy non-RL policy
        if self.state == self.lastState:
            chosenAction = random.choice(self.ACTIONS)  # TODO: use np.random
        else:
            chosenAction = self.lastAction
        self.lastAction = chosenAction
        self.lastState = self.state
        return chosenAction
