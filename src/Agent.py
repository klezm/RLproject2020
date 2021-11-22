import numpy as np
from functools import cache
import random

from Memory import Memory
from EpsilonGreedyPolicy import EpsilonGreedyPolicy
from myFuncs import cached_power, matrix_like, hRange, wRange, evaluate, assign


class Agent:
    """Reinforcement learner interacting with an Environment object and passing information to a GUI."""
    # RL variables:
    UP = (-1,0)  # actions and states are defined as tuples (not as lists), so they can be used as dict keys
    DOWN = (1,0)
    LEFT = (0,-1)
    RIGHT = (0,1)
    STRAIGHT_ACTIONSPACE = [UP, DOWN, LEFT, RIGHT]  # for iteration purposes
    UPLEFT = (-1,-1)
    UPRIGHT = (-1,1)
    DOWNLEFT = (1,-1)
    DOWNRIGHT = (1,1)
    DIAGONAL_ACTIONSPACE = [UPLEFT, UPRIGHT, DOWNLEFT, DOWNRIGHT]
    IDLE = (0,0)
    IDLE_ACTIONSPACE = [IDLE]

    # Flow control states passed to the GUI:
    UPDATED_BY_PLANNING = "Planning Update"
    UPDATED_BY_EXPERIENCE = "Experience Update"
    TOOK_ACTION = "Action Taken"
    FINISHED_EPISODE = "Episode Finish"
    STARTED_EPISODE = "Episode Start"
    OPERATIONS = [UPDATED_BY_PLANNING, UPDATED_BY_EXPERIENCE, TOOK_ACTION, FINISHED_EPISODE, STARTED_EPISODE]  # for iteration purposes

    @classmethod
    @cache
    def create_actionspace(cls, straight=True, diagonal=True, idle=True):
        actionspace = []
        if straight:
            actionspace += cls.STRAIGHT_ACTIONSPACE
        if diagonal:
            actionspace += cls.DIAGONAL_ACTIONSPACE
        if idle:
            actionspace += cls.IDLE_ACTIONSPACE
        return actionspace

    def __init__(self, environment, use_straightActions, use_diagonalActions, use_idleActions, currentReturnVar, currentEpisodeVar, learningRateVar,
                 dynamicAlphaVar, discountVar, nStepVar, nPlanVar, onPolicyVar, updateByExpectationVar, behaviorEpsilonVar, behaviorEpsilonDecayRateVar,
                 targetEpsilonVar, targetEpsilonDecayRateVar, decayEpsilonEpisodeWiseVar, initialActionvalueMean, initialActionvalueSigma, actionPlan=[]):
        self.environment = environment
        self.actionspace = self.create_actionspace(use_straightActions, use_diagonalActions, use_idleActions)
        self.currentReturnVar = currentReturnVar
        self.currentEpisodeVar = currentEpisodeVar
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
        self.initialActionvalueMean = initialActionvalueMean
        self.initialActionvalueSigma = initialActionvalueSigma
        self.Qvalues = matrix_like(self.environment.get_grid())
        self.greedyActions = matrix_like(self.environment.get_grid())
        self.model = matrix_like(self.environment.get_grid())
        self.visitedStateActionPairs = set()
        self.stateActionPairCounts = matrix_like(self.environment.get_grid())
        self.stateAbsenceCounts = np.zeros_like(self.environment.get_grid(), dtype=np.int32)  # using numpy since counting can be vectorized
        # self.stateActionPairAbsenceCounts = np.empty_like(self.environment.get_grid(), dtype=dict)  # will be needed for Dyna-Q+
        self._initialize_tables()
        # Strictly speaking, the agent has no model at all and therefore in the beginning knows nothing about the environment, including its shape.
        # But to avoid technical details in implementation that would anyway not change the Agent behavior at all,
        # the agent will be given that the states can be structured in a matrix that has the same shape as the environment
        # and that the actionspace is constant for all possible states.
        self.state = None
        self.episodeFinished = False
        self.episodeReturns = [0]
        self.stepReturns = [0]
        self.currentEpisodeVar.set(0)
        self.memory = Memory(self)
        self.hasChosenExploratoryAction = None
        self.hasMadeExploratoryAction = None
        self.targetAction = None
        self.targetActionvalue = None
        self.iSuccessivePlannings = None
        # Debug variables:
        self.actionPlan = actionPlan
        self.actionHistory = []

    def operate(self):
        if self.get_memory_size() >= self.nStepVar.get() >= 1 or (self.episodeFinished and self.get_memory_size()):
            # First condition is never True for MC
            self._process_earliest_memory()
            return self.UPDATED_BY_EXPERIENCE
        elif self.episodeFinished:
            self.episodeReturns.append(self.currentReturnVar.get())
            self.hasMadeExploratoryAction = False  # So at the next start the agent isnt colored exploratory anymore
            self.state = self.environment.remove_agent()
            self.memory.yield_lastForgottenState()  # for correct trace visualization
            self.episodeFinished = False
            return self.FINISHED_EPISODE
        elif self.state is None:
            self._start_episode()
            return self.STARTED_EPISODE
        elif self.iSuccessivePlannings < self.nPlanVar.get() and self.visitedStateActionPairs:
            self._plan()  # Model Algo needs no Memory and doesnt need to pass a target action to the behavior action. Nevertheless, expected version is possible.
            self.iSuccessivePlannings += 1
            return self.UPDATED_BY_PLANNING
        else:
            self._take_action()
            self.stepReturns.append(self.currentReturnVar.get())
            return self.TOOK_ACTION

    def _initialize_tables(self):
        for h in hRange(self.Qvalues):
            for w in wRange(self.Qvalues):
                self.Qvalues[h][w] = {action: np.random.normal(self.initialActionvalueMean, self.initialActionvalueSigma)
                                     for action in self.get_actionspace()}
                self._update_greedy_actions((h, w))
                self.stateActionPairCounts[h][w] = {action: 0 for action in self.get_actionspace()}
                self.model[h][w] = {action: (None, None) for action in self.get_actionspace()}

    def _update_greedy_actions(self, state: tuple):
        maxActionValue = max(evaluate(self.Qvalues, state).values())
        actionList = [action for action, value in evaluate(self.Qvalues, state).items() if value == maxActionValue]
        assign(self.greedyActions, state, actionList)

    def _set_Q(self, S: tuple, A: tuple, value: float):
        QvaluesForS = evaluate(self.Qvalues, S)
        QvaluesForS[A] = value
        self._update_greedy_actions(state=S)

    def _get_Q(self, S, A):
        return evaluate(self.Qvalues, S)[A]

    def _start_episode(self):
        self.targetAction = None
        self.currentReturnVar.set(0)
        self.currentEpisodeVar.set(self.currentEpisodeVar.get() + 1)
        self.iSuccessivePlannings = 0
        self.stateAbsenceCounts.fill(0)  # this is only used for visualizing the trace of the agent! Never reset at this point a count that is used for MC or Dyna-Q!
        self.state = self.environment.give_initial_position()
        if self.state is None:
            raise RuntimeError("No Starting Point found")

    def _take_action(self):
        self.iSuccessivePlannings = 0
        self.stateAbsenceCounts += 1
        behaviorAction = self._generate_behavior_action()
        reward, successorState, self.episodeFinished = self.environment.apply_action(behaviorAction)  # This is the only place where the agent exchanges information with the environment
        self.currentReturnVar.set(self.currentReturnVar.get() + reward)
        evaluate(self.model, self.state)[behaviorAction] = (successorState, reward)
        self.memory.memorize(self.state, behaviorAction, reward)
        self.visitedStateActionPairs.add((self.state, behaviorAction))  # enables efficient random choice of already visited state-action-pairs for Dyna-Q
        self.stateAbsenceCounts[successorState] = 0
        self.hasMadeExploratoryAction = self.hasChosenExploratoryAction  # if hasChosenExploratoryAction would be the only indicator for changing the agent color in the next visualization, then in the on-policy case, if the target was chosen to be an exploratory move in the last step-call, the coloring would happen BEFORE the move was taken, since in this line, the behavior action would already be determined and just copied from that target action with no chance to track if it was exploratory or not.
        self.state = successorState  # must happen after memorize and before generate_target!
        self._generate_target()
        if not self.decayEpsilonEpisodeWiseVar.get() or self.episodeFinished:
            self.behaviorPolicy.decay_epsilon()
            self.targetPolicy.decay_epsilon()
        # self.actionHistory.append(behaviorAction)  TODO: Dont forget debug stuff here
        # print(self.actionHistory)

    def _generate_behavior_action(self):
        if self.onPolicyVar.get() and self.targetAction:
            # In this case, the target action was chosen by the behavior policy (which is the only policy in on-policy) beforehand.
            return self.targetAction
        else:  # This will be executed if one of the following applies:
            # ...the updates are off policy, so the behavior action will NOT be copied from a previously chosen target action.
            # ...there is no recent target action because: the _value used for the latest update was an expectation OR no update happened in this episode so far.
            return self.behaviorPolicy.generate_action(self.state)

    def _generate_target(self):
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
            self.targetActionvalue = self._get_Q(S=self.state, A=self.targetAction)

    def _process_earliest_memory(self):
        correspondingState, actionToUpdate, _ = self.memory.get_oldest_memory()
        discountedRewardSum = self.memory.get_discountedRewardSum()
        self._update_actionvalue(actionToUpdate, correspondingState, discountedRewardSum, self.targetActionvalue, self.nStepVar.get())
        self.memory.forget_oldest_memory()

    def _update_actionvalue(self, actionToUpdate, correspondingState, discountedRewardSum, targetActionvalue, nStep):
        # step by step, so you can watch exactly whats happening when using a debugger
        Qbefore = self._get_Q(S=correspondingState, A=actionToUpdate)
        discountedTargetActionValue = cached_power(self.discountVar.get(), nStep) * targetActionvalue  # in the MC case (n is 0 here) the targetActionvalue is zero anyway, so it doesnt matter what n is.
        returnEstimate = discountedRewardSum + discountedTargetActionValue
        TD_error = returnEstimate - Qbefore
        if self.dynamicAlphaVar.get():
            actionCountDict = evaluate(self.stateActionPairCounts, correspondingState)
            actionCountDict[actionToUpdate] += 1  # works because dicts are mutable so the evaluation above yields a "pointer" to the dict
            self.learningRateVar.set(1/actionCountDict[actionToUpdate])
        update = self.learningRateVar.get() * TD_error
        Qafter = Qbefore + update
        self._set_Q(S=correspondingState, A=actionToUpdate, value=Qafter)

    def _plan(self):
        # TODO: Use efficient data structure as long as unvisited state-actions are not choosable. Alternative: all are choosable, but initialized with model(S,A)=S,0
        correspondingState, actionToUpdate = random.choice(tuple(self.visitedStateActionPairs))
        successorState, reward = evaluate(self.model, correspondingState)[actionToUpdate]
        if self.updateByExpectationVar.get():
            targetActionvalue = self.targetPolicy.get_expected_actionvalue(successorState)
        else:
            targetAction = self.targetPolicy.generate_action(successorState)
            targetActionvalue = self._get_Q(S=successorState, A=targetAction)
        self._update_actionvalue(actionToUpdate, correspondingState, reward, targetActionvalue, nStep=1)

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

    def get_targetAction(self):
        return self.targetAction

    def get_memory(self):
        return self.memory

    def get_memory_size(self):
        return len(self.memory)

    def get_actionspace(self):
        return self.actionspace
