import numpy as np
import random

from Memory import Memory
from EpsilonGreedyPolicy import EpsilonGreedyPolicy
from myFuncs import cached_power


class Agent:
    UP = (0,-1)
    DOWN = (0,1)
    LEFT = (-1,0)
    RIGHT = (1,0)
    ACTIONSPACE = [UP, DOWN, LEFT, RIGHT]

    def __init__(self, environment, learningRate, dynamicAlpha, discount, nStep, onPolicy, updateByExpectation,
                 behaviorEpsilon, behaviorEpsilonDecayRate, targetEpsilon, targetEpsilonDecayRate,
                 initialActionvalueMean=0, initialActionvalueSigma=0, predefinedAlgorithm=None, actionPlan=[], **kwargs):
        self.environment = environment
        if predefinedAlgorithm:
            # TODO: set missing params accordingly
            pass
        self.learningRate = learningRate
        self.dynamicAlpha = dynamicAlpha
        self.discount = discount
        self.behaviorPolicy = EpsilonGreedyPolicy(self, behaviorEpsilon, behaviorEpsilonDecayRate)
        self.targetPolicy = EpsilonGreedyPolicy(self, targetEpsilon, targetEpsilonDecayRate)
        self.onPolicy = onPolicy
        self.updateByExpectation = updateByExpectation
        self.nStep = nStep
        self.initialActionvalueMean = initialActionvalueMean
        self.initialActionvalueSigma = initialActionvalueSigma
        self.Qvalues = np.empty_like(self.environment.get_grid())  # must be kept over episodes
        self.greedyActions = np.empty_like(self.environment.get_grid())
        self.initialize_actionvalues()
        self.stateActionPairCounts = np.empty_like(self.environment.get_grid())
        self.initialize_state_action_pair_counts()
        self.episodicTask = None  # TODO: This variable is not used so far.
        self.episodeFinished = True
        self.state = None
        self.return_ = None  # underscore to avoid naming conflict with return keyword
        self.episodeReturns = []
        self.memory = Memory(self)
        self.hasChosenExploratoryMove = None
        self.hasMadeExploratoryMove = None
        self.targetAction = None
        # Debug variables:
        self.actionPlan = actionPlan
        self.actionHistory = []

    def get_discount(self):
        return self.discount.get()

    def get_episodeReturns(self):
        return self.episodeReturns

    def initialize_actionvalues(self):
        for x in range(self.Qvalues.shape[0]):
            for y in range(self.Qvalues.shape[1]):
                self.Qvalues[x,y] = {action: np.random.normal(self.initialActionvalueMean, self.initialActionvalueSigma)
                                      for action in self.ACTIONSPACE}
                self.update_greedy_actions((x,y))

    def initialize_state_action_pair_counts(self):
        for x in range(self.stateActionPairCounts.shape[0]):
            for y in range(self.stateActionPairCounts.shape[1]):
                self.stateActionPairCounts[x,y] = {action: 0 for action in self.ACTIONSPACE}

    def get_state(self):
        return self.state

    def get_Qvalues(self):
        return self.Qvalues

    def get_greedyActions(self):
        return self.greedyActions

    def get_Q(self, S, A):
        return self.Qvalues[S][A]

    def set_Q(self, S, A, value):
        self.Qvalues[S][A] = value
        self.update_greedy_actions(state=S)

    def update_greedy_actions(self, state):
        maxActionValue = max(self.Qvalues[state].values())
        self.greedyActions[state] = [action for action, value in self.Qvalues[state].items() if value == maxActionValue]

    def start_episode(self):
        self.episodeFinished = False
        self.targetAction = None
        self.return_ = 0
        self.state = self.environment.give_initial_position()
        if self.state is None:
            raise RuntimeError("No Starting Point found")

    def step(self):
        behaviorAction = self.generate_behavior_action(self.state)
        reward, successorState, self.episodeFinished = self.environment.apply_action(behaviorAction)
        self.hasMadeExploratoryMove = self.hasChosenExploratoryMove  # if hasChosenExploratoryMove would be the only indicator for changing the agent color in the next visualization, then in the on-policy case, if the target was chosen to be an exploratory move in the last step-call, the coloring would happen BEFORE the move was taken, since in this line, the behavior action would already be determined and just copied from that target action with no chance to track if it was exploratory or not.
        self.memory.memorize(self.state, behaviorAction, reward)
        self.return_ += reward  # underscore at the end because "return" is a python keyword
        self.state = successorState
        if self.episodeFinished:
            self.episodeReturns.append(self.return_)
            return
        targetActionvalue = self.generate_target(self.state)
        if self.memory.get_size() == self.nStep.get():
            self.update_actionvalue(targetActionvalue)
        self.behaviorPolicy.decay_epsilon()
        self.targetPolicy.decay_epsilon()
        # self.actionHistory.append(behaviorAction)  TODO: Dont forget debug stuff here
        # print(self.actionHistory)

    def update_actionvalue(self, targetActionvalue):
        # step by step, so you can watch exactly whats happening when using a debugger
        discountedRewardSum = self.memory.get_discountedRewardSum()
        actionToUpdate, correspondingState = self.memory.pop_oldest_state_action()
        Qbefore = self.get_Q(S=correspondingState, A=actionToUpdate)
        discountedTargetActionValue = cached_power(self.discount.get(), self.nStep.get()) * targetActionvalue  # in the MC case (N is -1 here) the targetctionvalue is zero anyway, so it doesnt matter what n is.
        returnEstimate = discountedRewardSum + discountedTargetActionValue
        TD_error = returnEstimate - Qbefore
        if self.dynamicAlpha.get():
            self.stateActionPairCounts[correspondingState][actionToUpdate] += 1
            self.learningRate.set(1/self.stateActionPairCounts[correspondingState][actionToUpdate])
        update = self.learningRate.get() * TD_error
        Qafter = Qbefore + update
        self.set_Q(S=correspondingState, A=actionToUpdate, value=Qafter)

    def process_earliest_memory(self, targetActionvalue=0):
        self.update_actionvalue(targetActionvalue=targetActionvalue)

    def generate_target(self, state):
        if self.onPolicy.get():
            policy = self.behaviorPolicy
        else:
            policy = self.targetPolicy
        if self.updateByExpectation.get():
            self.targetAction = None  # Otherwise, if switched dynamically to expectation during an episode, in the On-Policy case, the actin selected in the else-block below would be copied and used as the behavior action in every following turn, resulting in an agent that cannot change its direction anymore
            return policy.get_expected_actionvalue(state)
        else:
            self.targetAction = policy.generate_action(state)
            return self.get_Q(S=state, A=self.targetAction)

    def generate_behavior_action(self, state):
        if self.onPolicy.get() and self.targetAction:
            # In this case, the target action was chosen by the behavior policy (which is the only policy in on-policy) beforehand.
            return self.targetAction
        else:  # This will be executed if one of the following applies:
            # ...the updates are off policy, so the behavior action will NOT be copied from a previously chosen target action.
            # ...there is no recent target action because: the value used for the latest update was an expectation OR no update happened in this episode so far.
            return self.behaviorPolicy.generate_action(state)

    def get_memory_size(self):
        return self.memory.get_size()
