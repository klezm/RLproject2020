import random

from Policy import Policy


class EpsilonGreedyPolicy(Policy):
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
            self.agent.hasChosenExploratoryMove = True
            return self.sample_random_action()
        else:
            self.agent.hasChosenExploratoryMove = False
            return self.give_greedy_action(state)
        
    def get_expected_actionvalue(self, state):
        # step by step:
        currentStateQvalueDict = self.agent.get_Qvalues()[state]
        greedyMean = currentStateQvalueDict[self.agent.get_greedyActions()[state][0]]
        # technically, for calculating the mean Qvalue of the greedy action choice, we have to average over all values of current greedy actions.
        # But since all greedy actions have by definition the same value (namely the maximum Qvalue of all currently available actions),
        # we can just set the Qvalue of our first listed greedy action as the mean.
        if self.epsilonVar.get():
            exploratoryMean = sum(currentStateQvalueDict.values()) / len(currentStateQvalueDict)
            return self.epsilonVar.get() * exploratoryMean + (1 - self.epsilonVar.get()) * greedyMean
        else:  # save computation time if policy is greedy (epsilon == 0)
            return greedyMean

    def decay_epsilon(self):
        self.epsilonVar.set(self.epsilonVar.get() * self.epsilonDecayRateVar.get())
