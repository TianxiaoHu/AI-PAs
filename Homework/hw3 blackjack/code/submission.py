import util, math, random
from collections import defaultdict
from util import ValueIteration

############################################################
# Problem 2a

# If you decide 2a is true, prove it in blackjack.pdf and put "return None" for
# the code blocks below.  If you decide that 2a is false, construct a counterexample.
class CounterexampleMDP(util.MDP):
    def startState(self):
        # BEGIN_YOUR_CODE (our solution is 1 line of code, but don't worry if you deviate from this)
        return 0
        # END_YOUR_CODE

    # Return set of actions possible from |state|.
    def actions(self, state):
        # BEGIN_YOUR_CODE (our solution is 1 line of code, but don't worry if you deviate from this)
        """
        In terminal state, we should return a empty list [], but it will raise an exception.
        But we only focus on start state - so let the terminal state return itself in implementation.
        """
        return [-1, 1] if state == 0 else [state]
        # END_YOUR_CODE

    # Return a list of (newState, prob, reward) tuples corresponding to edges
    # coming out of |state|.
    def succAndProbReward(self, state, action):
        # BEGIN_YOUR_CODE (our solution is 1 line of code, but don't worry if you deviate from this)
        return [(-1, 0.9, 10),(1, 0.1, 100)] if state == 0 else [(state, 1, 0)]
        # END_YOUR_CODE

    def discount(self):
        # BEGIN_YOUR_CODE (our solution is 1 line of code, but don't worry if you deviate from this)
        return 1
        # END_YOUR_CODE

############################################################
# Problem 3a

class BlackjackMDP(util.MDP):
    def __init__(self, cardValues, multiplicity, threshold, peekCost):
        """
        cardValues: array of card values for each card type
        multiplicity: number of each card type
        threshold: maximum total before going bust
        peekCost: how much it costs to peek at the next card
        """
        self.cardValues = cardValues
        self.multiplicity = multiplicity
        self.threshold = threshold
        self.peekCost = peekCost

    # Return the start state.
    # Look at this function to learn about the state representation.
    # The first element of the tuple is the sum of the cards in the player's
    # hand.
    # The second element is the index (not the value) of the next card, if the player peeked in the
    # last action.  If they didn't peek, this will be None.
    # The final element is the current deck.
    def startState(self):
        return (0, None, (self.multiplicity,) * len(self.cardValues))  # total, next card (if any), multiplicity for each card

    # Return set of actions possible from |state|.
    # You do not need to modify this function.
    # All logic for dealing with end states should be done in succAndProbReward
    def actions(self, state):
        return ['Take', 'Peek', 'Quit']

    # Return a list of (newState, prob, reward) tuples corresponding to edges
    # coming out of |state|.  Indicate a terminal state (after quitting or
    # busting) by setting the deck to None.
    # When the probability is 0 for a particular transition, don't include that
    # in the list returned by succAndProbReward.
    def succAndProbReward(self, state, action):
        # BEGIN_YOUR_CODE (our solution is 53 lines of code, but don't worry if you deviate from this)
        totalValue, peekedIndex, deckCardNum = state
        if deckCardNum == None or sum(deckCardNum) == 0:
            return []

        allStates = []
        if action == 'Quit':
            return [((totalValue, None, None), 1, totalValue)]

        if action == 'Peek':
            if peekedIndex:
                return []
            else:
                totalCardNum = sum(deckCardNum)
                for i in range(0, len(deckCardNum)):
                    if deckCardNum[i]:
                        peeked = i
                        peekProb = float(deckCardNum[peeked]) / totalCardNum
                        allStates.append(((totalValue, peeked, deckCardNum), peekProb, -self.peekCost))
            return allStates

        if action == 'Take':
            if peekedIndex:
                newTotalValue = totalValue + self.cardValues[peekedIndex]
                if newTotalValue > self.threshold:
                    return [((newTotalValue, None, None), 1, 0)]
                else:
                    newDeckCardNum = list(deckCardNum)
                    newDeckCardNum[peekedIndex] -= 1
                    newDeckCardNum = tuple(newDeckCardNum)
                    if sum(newDeckCardNum) == 0:
                        return [((newTotalValue, None, None), 1, newTotalValue)]
                    else:
                        return [((newTotalValue, None, newDeckCardNum), 1, 0)]
            else:
                totalCardNum = sum(deckCardNum)
                for i in range(0, len(deckCardNum)):
                    if deckCardNum[i]:
                        selected = i
                        selectProb = float(deckCardNum[selected]) / totalCardNum
                        newTotalValue = totalValue + self.cardValues[selected]
                        if newTotalValue > self.threshold:
                            allStates.append(((newTotalValue, None, None), selectProb, 0))
                        else:
                            newDeckCardNum = list(deckCardNum)
                            newDeckCardNum[selected] -= 1
                            newDeckCardNum = tuple(newDeckCardNum)
                            if sum(newDeckCardNum) == 0:
                                allStates.append(((newTotalValue, None, None), selectProb, newTotalValue))
                            else:
                                allStates.append(((newTotalValue, None, newDeckCardNum), selectProb, 0))
                return allStates
        # END_YOUR_CODE

    def discount(self):
        return 1

############################################################
# Problem 3b

def peekingMDP():
    """
    Return an instance of BlackjackMDP where peeking is the optimal action at
    least 10% of the time.
    """
    # BEGIN_YOUR_CODE (our solution is 2 lines of code, but don't worry if you deviate from this)
    return BlackjackMDP(cardValues=[2, 3, 4, 5, 6, 100], multiplicity=1, threshold=20, peekCost=1)
    # END_YOUR_CODE

############################################################
# Problem 4a: Q learning

# Performs Q-learning.  Read util.RLAlgorithm for more information.
# actions: a function that takes a state and returns a list of actions.
# discount: a number between 0 and 1, which determines the discount factor
# featureExtractor: a function that takes a state and action and returns a list of (feature name, feature value) pairs.
# explorationProb: the epsilon value indicating how frequently the policy
# returns a random action
class QLearningAlgorithm(util.RLAlgorithm):
    def __init__(self, actions, discount, featureExtractor, explorationProb=0.2):
        self.actions = actions
        self.discount = discount
        self.featureExtractor = featureExtractor
        self.explorationProb = explorationProb
        self.weights = defaultdict(float)
        self.numIters = 0

    # Return the Q function associated with the weights and features
    def getQ(self, state, action):
        score = 0
        for f, v in self.featureExtractor(state, action):
            score += self.weights[f] * v
        return score

    # This algorithm will produce an action given a state.
    # Here we use the epsilon-greedy algorithm: with probability
    # |explorationProb|, take a random action.
    def getAction(self, state):
        self.numIters += 1
        if random.random() < self.explorationProb:
            return random.choice(self.actions(state))
        else:
            return max((self.getQ(state, action), action) for action in self.actions(state))[1]

    # Call this function to get the step size to update the weights.
    def getStepSize(self):
        return 1.0 / math.sqrt(self.numIters)

    # We will call this function with (s, a, r, s'), which you should use to update |weights|.
    # Note that if s is a terminal state, then s' will be None.  Remember to check for this.
    # You should update the weights using self.getStepSize(); use
    # self.getQ() to compute the current estimate of the parameters.
    def incorporateFeedback(self, state, action, reward, newState):
        # BEGIN_YOUR_CODE (our solution is 12 lines of code, but don't worry if you deviate from this)
        Vopt = 0
        if newState != None:
            Vopt = max((self.getQ(newState, nextAction), nextAction) for nextAction in self.actions(newState))[0]
        prediction = self.getQ(state,action)
        target = reward + self.discount * Vopt
        eta = self.getStepSize()
        scale = eta * (prediction - target)
        for f, v in self.featureExtractor(state, action):
            self.weights[f] = self.weights[f] - scale * v
        # END_YOUR_CODE

# Return a singleton list containing indicator feature for the (state, action)
# pair.  Provides no generalization.
def identityFeatureExtractor(state, action):
    featureKey = (state, action)
    featureValue = 1
    return [(featureKey, featureValue)]

############################################################
# Problem 4b: convergence of Q-learning
# Small test case
smallMDP = BlackjackMDP(cardValues=[1, 5], multiplicity=2, threshold=10, peekCost=1)

# Large test case
largeMDP = BlackjackMDP(cardValues=[1, 3, 5, 8, 10], multiplicity=3, threshold=40, peekCost=1)
largeMDP.computeStates()

############################################################
# Problem 4c: features for Q-learning.

# You should return a list of (feature key, feature value) pairs (see
# identityFeatureExtractor()).
# Implement the following features:
# - indicator on the total and the action (1 feature).
# - indicator on the presence/absence of each card and the action (1 feature).
#       Example: if the deck is (3, 4, 0 , 2), then your indicator on the presence of each card is (1,1,0,1)
#       Only add this feature if the deck != None
# - indicator on the number of cards for each card type and the action (len(counts) features).  Only add these features if the deck != None
def blackjackFeatureExtractor(state, action):
    totalValue, peekedIndex, deckCardNum = state
    # BEGIN_YOUR_CODE (our solution is 9 lines of code, but don't worry if you deviate from this)
    arr = []
    arr.append((('total_feature', totalValue, action), 1))
    if deckCardNum != None:
        arr.append((('card_presense', tuple([1 if x else 0 for x in deckCardNum]), action), 1))
    if deckCardNum != None:
        for i in range(0,len(deckCardNum)):
            arr.append((('num_cards', i, deckCardNum[i], action), 1))
    return arr
    # END_YOUR_CODE

############################################################
# Problem 4d: What happens when the MDP changes underneath you?!

# Original mdp
originalMDP = BlackjackMDP(cardValues=[1, 5], multiplicity=2, threshold=10, peekCost=1)

# New threshold
newThresholdMDP = BlackjackMDP(cardValues=[1, 5], multiplicity=2, threshold=15, peekCost=1)
