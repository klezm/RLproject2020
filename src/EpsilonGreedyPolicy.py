import random

from Policy import Policy
from myFuncs import evaluate


class EpsilonGreedyPolicy(Policy):
    """ε-greedy policy as introduced in Sutton & Barto.
    ε defines the probability of using a random action
    over a greedy action and may be altered over time.
    """
    def __init__(self, agent, epsilonVar, epsilonDecayRateVar):
        # Epsilon = 0 equals the greedy policy
        super().__init__(agent)
        self.epsilonVar = epsilonVar
        self.epsilonDecayRateVar = epsilonDecayRateVar
        
    def generate_action(self, state):
        # debug:
        #if self.agent.actionPlan:
        #    return self.agent.actionPlan.pop(0)
        if self.epsilonVar.get() and random.random() < self.epsilonVar.get():  # only use rng if necessary
            self.agent.hasChosenExploratoryAction = True
            return self.sample_random_action()
        else:
            self.agent.hasChosenExploratoryAction = False
            return self.give_greedy_action(state)
        
    def get_expected_actionvalue(self, state):
        # step by step:
        currentStateQvalueDict = evaluate(self.agent.get_Qvalues(), state)
        currentStateGreedyAction = evaluate(self.agent.get_greedyActions(), state)[0]
        greedyMean = currentStateQvalueDict[currentStateGreedyAction]
        # technically, for calculating the mean Qvalue of the greedy action choice, we have to average over all values of current greedy actions.
        # But since all greedy actions have by definition the same _value (namely the maximum Qvalue of all currently available actions),
        # we can just set the Qvalue of our first listed greedy action as the mean.
        if self.epsilonVar.get():
            exploratoryMean = sum(currentStateQvalueDict.values()) / len(currentStateQvalueDict)
            return self.epsilonVar.get() * exploratoryMean + (1 - self.epsilonVar.get()) * greedyMean
        else:  # save computation time if policy is greedy (epsilon == 0)
            return greedyMean

    def decay_epsilon(self):
        newEpsilon = self.epsilonVar.get() * self.epsilonDecayRateVar.get()
        if newEpsilon < 1e-04:  # otherwise, the value would be shown in scientific notation with way too much digits, so that the exponent wouldnt be visible anymore in the entry
            newEpsilon = 0.
        self.epsilonVar.set(newEpsilon)
