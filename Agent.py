import numpy as np

from Memory import Memory
from EpsilonGreedyPolicy import EpsilonGreedyPolicy
from myFuncs import cached_power


class Agent:
    # RL variables:
    UP = (0,-1)  # actions and states are defined as tuples (not as lists), so they can be used as dict keys
    DOWN = (0,1)
    LEFT = (-1,0)
    RIGHT = (1,0)
    UPLEFT = (-1,-1)
    UPRIGHT = (1,-1)
    DOWNLEFT = (-1,1)
    DOWNRIGHT = (1,1)
    IDLE = (0,0)
    DEFAULT_ACTIONSPACE = [UP, DOWN, LEFT, RIGHT]  # for iteration purposes
    KING_EXCLUSIVE_ACTIONSPACE = [UPLEFT, UPRIGHT, DOWNLEFT, DOWNRIGHT]
    IDLE_ACTIONSPACE = [IDLE]
    EXTENDED_ACTIONSPACE = DEFAULT_ACTIONSPACE + KING_EXCLUSIVE_ACTIONSPACE

    # Flow control variables to pass to an external GUI:
    UPDATED_BY_PLANNING = "Planning Update"
    UPDATED_BY_EXPERIENCE = "Experience Update"
    TOOK_ACTION = "Action Taken"
    FINISHED_EPISODE = "Episode Finish"
    STARTED_EPISODE = "Episode Start"
    OPERATIONS = [UPDATED_BY_PLANNING, UPDATED_BY_EXPERIENCE, TOOK_ACTION, FINISHED_EPISODE, STARTED_EPISODE]  # for iteration purposes

    def __init__(self, environment, use_kingMoves, currentReturnVar, learningRateVar, dynamicAlphaVar, discountVar, nStepVar, nPlanVar, onPolicyVar,
                 updateByExpectationVar, behaviorEpsilonVar, behaviorEpsilonDecayRateVar, targetEpsilonVar, targetEpsilonDecayRateVar,
                 decayEpsilonEpisodeWiseVar, initialActionvalueMean, initialActionvalueSigma, predefinedAlgorithm=None, actionPlan=[]):
        self.environment = environment
        if use_kingMoves:
            self.actionspace = self.EXTENDED_ACTIONSPACE
        else:
            self.actionspace = self.DEFAULT_ACTIONSPACE
        if predefinedAlgorithm:
            # TODO: set missing params accordingly
            pass
        self.currentReturnVar = currentReturnVar
        self.learningRateVar = learningRateVar
        self.dynamicAlphaVar = dynamicAlphaVar
        self.discountVar = discountVar
        self.behaviorPolicy = EpsilonGreedyPolicy(self, behaviorEpsilonVar, behaviorEpsilonDecayRateVar)
        self.targetPolicy = EpsilonGreedyPolicy(self, targetEpsilonVar, targetEpsilonDecayRateVar)
        self.decayEpsilonEpisodeWiseVar = decayEpsilonEpisodeWiseVar
        self.onPolicyVar = onPolicyVar
        self.updateByExpectationVar = updateByExpectationVar
        self.nStepVar = nStepVar
        self.nPlanVar = nPlanVar
        self.initialActionvalueMean = initialActionvalueMean  # TODO: Set this in GUI
        self.initialActionvalueSigma = initialActionvalueSigma  # TODO: Set this in GUI
        self.Qvalues = np.empty_like(self.environment.get_grid(), dtype=dict)
        self.greedyActions = np.empty_like(self.environment.get_grid(), dtype=list)
        self.stateActionPairCounts = np.empty_like(self.environment.get_grid(), dtype=dict)
        self.stateAbsenceCounts = np.zeros_like(self.environment.get_grid(), dtype=np.int32)
        self.initialize_tables()
        # Strictly speaking, the agent has no model at all and therefore in the beginning knows nothing about the environment, including its shape.
        # But to avoid technical details in implementation that would anyway not change the Agent behavior at all,
        # the agent will be given that the states can be structured in a matrix that has the same shape as the environment
        # and that the actionspace is constant for all possible states.
        self.state = None
        self.episodeFinished = False
        self.episodeReturns = [0]
        self.stepReturns = [0]
        self.memory = Memory(self)
        self.hasChosenExploratoryMove = None
        self.hasMadeExploratoryMove = None
        self.targetAction = None
        self.targetActionvalue = None
        self.iSuccessivePlannings = None
        # Debug variables:
        self.actionPlan = actionPlan
        self.actionHistory = []

    def initialize_tables(self):
        for x in range(self.Qvalues.shape[0]):
            for y in range(self.Qvalues.shape[1]):
                self.Qvalues[x,y] = {action: np.random.normal(self.initialActionvalueMean, self.initialActionvalueSigma)
                                     for action in self.get_actionspace()}
                self.update_greedy_actions((x,y))
                self.stateActionPairCounts[x,y] = {action: 0 for action in self.get_actionspace()}

    def update_greedy_actions(self, state: tuple):
        maxActionValue = max(self.Qvalues[state].values())
        self.greedyActions[state] = [action for action, value in self.Qvalues[state].items() if value == maxActionValue]

    #def set_Q(self, S: Tuple, A: tuple, value: float):  # TODO: import Tuple from typing
    def set_Q(self, S: tuple, A: tuple, value: float):
        self.Qvalues[S][A] = value
        self.update_greedy_actions(state=S)

    def operate(self):
        if self.get_memory_size() >= self.nStepVar.get() >= 1 or (self.episodeFinished and self.get_memory_size()):
            # First condition is never True for MC
            self.process_earliest_memory()
            return self.UPDATED_BY_EXPERIENCE
        elif self.episodeFinished:
            self.episodeReturns.append(self.currentReturnVar.get())
            self.hasMadeExploratoryMove = False  # So at the next start the agent isnt colored exploratory anymore
            self.state = self.environment.remove_agent()
            self.memory.yield_lastForgottenState()  # for correct trace visualization
            self.episodeFinished = False
            return self.FINISHED_EPISODE
        elif self.state is None:
            self.start_episode()
            return self.STARTED_EPISODE
        elif self.iSuccessivePlannings < self.nPlanVar.get():
            self.plan()  # TODO: Model Algo needs no Memory and doesnt need to pass a target action to the behavior action. Nevertheless, expected version is possible.
            self.iSuccessivePlannings += 1
            return self.UPDATED_BY_PLANNING
        else:
            self.take_action()
            self.stepReturns.append(self.currentReturnVar.get())
            return self.TOOK_ACTION

    def start_episode(self):
        self.targetAction = None
        self.currentReturnVar.set(0)
        self.iSuccessivePlannings = 0
        self.stateAbsenceCounts *= 0  # is this faster then re-initializing the whole array?
        self.state = self.environment.give_initial_position()
        if self.state is None:
            raise RuntimeError("No Starting Point found")

    def take_action(self):
        self.stateAbsenceCounts += 1
        self.iSuccessivePlannings = 0
        behaviorAction = self.generate_behavior_action()
        reward, successorState, self.episodeFinished = self.environment.apply_action(behaviorAction)  # This is the only place where the agent exchanges information with the environment
        self.hasMadeExploratoryMove = self.hasChosenExploratoryMove  # if hasChosenExploratoryMove would be the only indicator for changing the agent color in the next visualization, then in the on-policy case, if the target was chosen to be an exploratory move in the last step-call, the coloring would happen BEFORE the move was taken, since in this line, the behavior action would already be determined and just copied from that target action with no chance to track if it was exploratory or not.
        self.memory.memorize(self.state, behaviorAction, reward)
        self.currentReturnVar.set(self.currentReturnVar.get() + reward)
        self.state = successorState  # must happen after memorize and before generate_target!
        self.stateAbsenceCounts[self.state] = 0
        self.generate_target()
        if not self.decayEpsilonEpisodeWiseVar.get() or self.episodeFinished:
            self.behaviorPolicy.decay_epsilon()
            self.targetPolicy.decay_epsilon()
        # self.actionHistory.append(behaviorAction)  TODO: Dont forget debug stuff here
        # print(self.actionHistory)

    def generate_behavior_action(self):
        if self.onPolicyVar.get() and self.targetAction:
            # In this case, the target action was chosen by the behavior policy (which is the only policy in on-policy) beforehand.
            return self.targetAction
        else:  # This will be executed if one of the following applies:
            # ...the updates are off policy, so the behavior action will NOT be copied from a previously chosen target action.
            # ...there is no recent target action because: the value used for the latest update was an expectation OR no update happened in this episode so far.
            return self.behaviorPolicy.generate_action(self.state)

    def generate_target(self):
        if self.episodeFinished:
            self.targetAction = None
            self.targetActionvalue = 0  # per definition
            return
        if self.onPolicyVar.get():
            policy = self.behaviorPolicy
        else:
            policy = self.targetPolicy
        if self.updateByExpectationVar.get():
            self.targetAction = None  # Otherwise, if switched dynamically to expectation during an episode, in the On-Policy case, the action selected in the else-block below would be copied and used as the behavior action in every following turn, resulting in an agent that cannot change its direction anymore
            self.targetActionvalue = policy.get_expected_actionvalue(self.state)
        else:
            self.targetAction = policy.generate_action(self.state)
            self.targetActionvalue = self.get_Q(S=self.state, A=self.targetAction)

    def process_earliest_memory(self):
        self.update_actionvalue()
        self.memory.forget_oldest_memory()

    def update_actionvalue(self):
        # step by step, so you can watch exactly whats happening when using a debugger
        discountedRewardSum = self.memory.get_discountedRewardSum()
        correspondingState, actionToUpdate, _ = self.memory.get_oldest_memory()
        Qbefore = self.get_Q(S=correspondingState, A=actionToUpdate)
        discountedTargetActionValue = cached_power(self.discountVar.get(), self.nStepVar.get()) * self.targetActionvalue  # in the MC case (n is -1 here) the targetActionvalue is zero anyway, so it doesnt matter what n is.
        returnEstimate = discountedRewardSum + discountedTargetActionValue
        TD_error = returnEstimate - Qbefore
        if self.dynamicAlphaVar.get():
            self.stateActionPairCounts[correspondingState][actionToUpdate] += 1
            self.learningRateVar.set(1/self.stateActionPairCounts[correspondingState][actionToUpdate])
        update = self.learningRateVar.get() * TD_error
        Qafter = Qbefore + update
        self.set_Q(S=correspondingState, A=actionToUpdate, value=Qafter)

    def plan(self):
        print(self.iSuccessivePlannings)

    def get_discount(self):
        return self.discountVar.get()

    def get_episodeReturns(self):
        return self.episodeReturns

    def get_stepReturns(self):
        return self.stepReturns

    def get_state(self):
        return self.state

    def get_Qvalues(self):
        return self.Qvalues

    def get_greedyActions(self):
        return self.greedyActions

    def get_absence(self, state):
        return self.stateAbsenceCounts[state]

    def get_Q(self, S, A):
        return self.Qvalues[S][A]

    def get_targetAction(self):
        return self.targetAction

    def get_memory(self):
        return self.memory

    def get_memory_size(self):
        return len(self.memory)

    def get_actionspace(self):
        return self.actionspace
