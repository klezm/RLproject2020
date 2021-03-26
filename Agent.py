import numpy as np
import random

from Memory import Memory


class Agent:
    UP = (0,-1)
    DOWN = (0,1)
    LEFT = (-1,0)
    RIGHT = (1,0)
    ACTIONS = [UP, DOWN, LEFT, RIGHT]

    def __init__(self, environment, stepSize, discount, lambda_, epsilon, epsilonDecayRate, onPolicy, initialActionvalueMean=0, initialActionvalueSigma=0, predefinedAlgorithm=None, actionPlan=[]):
        self.environment = environment
        if predefinedAlgorithm:
            # TODO: set missing params accordingly
            pass
        self.stepSize = stepSize
        self.discount = discount
        self.initial_epsilon = float(epsilon.get())
        self.current_epsilon = epsilon
        self.epsilonDecayRate = epsilonDecayRate
        self.lambda_ = lambda_
        self.onPolicy = onPolicy
        self.initialActionvalueMean = initialActionvalueMean
        self.initialActionvalueSigma = initialActionvalueSigma
        self.Qvalues = np.empty_like(self.environment.grid)  # must be kept over episodes  # TODO: getter
        self.initialize_actionvalues()
        self.episodicTask = None  # Todo: This variable is not used so far. Find out if Return is still a thing in non episodic task, and if, is it defined with or without discount?
        self.episodeFinished = True
        self.state = None
        self.return_ = None  # underscore to avoid naming conflict with return keyword
        self.episodeReturns = np.array([])  # must be kept over episodes
        self.memory = Memory()
        # Debug variables:
        self.actionPlan = actionPlan
        self.actionHistory = []

    def get_episode_returns(self):
        return self.episodeReturns

    def initialize_actionvalues(self):
        for x in range(self.Qvalues.shape[0]):
            for y in range(self.Qvalues.shape[1]):
                self.Qvalues[x, y] = {action: np.random.normal(self.initialActionvalueMean, self.initialActionvalueSigma) for action in self.ACTIONS}

    def get_state(self):
        return self.state

    def get_Qvalues(self):
        return self.Qvalues

    def Q(self, S, A):
        return self.Qvalues[S][A]

    def start_episode(self):
        self.episodeFinished = False
        self.return_ = 0
        self.state = self.environment.give_initial_position()
        if self.state is None:
            raise RuntimeError("No Starting Point found")

    def step(self):
        #print(self.return_)
        behaviorAction = self.behavior_policy()
        if self.onPolicy.get():
            targetAction = behaviorAction
        else:
            targetAction = self.target_policy()
        targetActionvalue = self.Q(S=self.state, A=targetAction)
        self.update_actionvalues(targetActionvalue)  # TODO: If below apply action, would I just have to remind last reward?
        reward, successorState, self.episodeFinished = self.environment.apply_action(behaviorAction)
        # self.actionHistory.append(behaviorAction)  TODO: Dont forget debug stuff here
        #print(self.actionHistory)
        self.memory.memorize_state_action_reward((self.state, behaviorAction, reward))
        self.state = successorState
        self.return_ += reward
        # Epsilon Decay
        if float(self.epsilonDecayRate.get()) != 1:  # save computation time instead of multiplying by 1
            self.current_epsilon.set(float(self.current_epsilon.get()) * float(self.epsilonDecayRate.get()))
        if self.episodeFinished:
            self.episodeReturns = np.append(self.episodeReturns, self.return_)

    def process_remaining_memory(self):
        while self.memory.get_size():  # TODO: This is doubled (once here, once in function), but a boolean return value for the function instead doesnt feel nice
            self.update_actionvalues(targetActionvalue=0)

    def update_actionvalues(self, targetActionvalue):
        if self.memory.get_size() >= int(self.lambda_.get()):
            actionToUpdate = self.memory.get_action(depth=int(self.lambda_.get()))
            correspondingState = self.memory.get_state(depth=int(self.lambda_.get()))
            correspondingReward = self.memory.get_reward(depth=int(self.lambda_.get()))  # Below: part after += in extra line
            Qbefore = self.Q(S=correspondingState, A=actionToUpdate)
            error = correspondingReward + float(self.discount.get()) * targetActionvalue - Qbefore
            update = float(self.stepSize.get()) * error
            Qafter = Qbefore + update
            self.Qvalues[correspondingState][actionToUpdate] = Qafter
            self.memory.forget_state_action_reward(depth=1)

    def target_policy(self):
        return self.get_greedy_action()

    def behavior_policy(self):
        if self.actionPlan:  # debug
            return self.actionPlan.pop(0)
        if np.random.rand() < float(self.current_epsilon.get()):
            return self.sample_random_action()
        else:
            return self.get_greedy_action()

    def get_greedy_action(self):
        maxActionValue = max(self.Qvalues[self.state].values())
        actionCandidates = [action for action, value in self.Qvalues[self.state].items() if value == maxActionValue]
        if len(actionCandidates) > 1:
            return actionCandidates[np.random.randint(len(actionCandidates))]
        else:  # to save computation time if result is deterministic anyway
            return actionCandidates[0]

    def sample_random_action(self):
        return self.ACTIONS[np.random.randint(len(self.ACTIONS))]
