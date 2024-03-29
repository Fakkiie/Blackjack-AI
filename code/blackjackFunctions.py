import numpy as np
import matplotlib as plt
import random

class hand:
    def __init__(self):
        self.cards = []
        self.handSum = 0
        self.ace_count = 0
    
    def addCard(self, card):
        new_card = card
        if (new_card.ace):
            self.ace_count += 1
        
        self.cards.append(card)
        self.handSum += card.value

        if self.handSum > 21 and self.ace_count > 0:
            self.handSum -= 10
            self.ace_count -= 1

        
    def resetHand(self):
        self.cards = []
        self.handSum = 0
        
        
class card:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit
        self.ace = (value == 11)
        
    def __repr__(self):
        return str(self.value) + self.suit[0]

class shoe:
    def __init__(self):
        self.cards = []
        self.shufflePoint = 0
        self.count = 0  # Initialize count for card counting
        for _ in np.arange(6):
            for i in [11,2,3,4,5,6,7,8,9,10,10,10,10]:
                for j in ['clubs', 'hearts', 'spades', 'diamonds']:
                    c = card(i,j)
                    self.cards.append(c)
        random.shuffle(self.cards)
                
    def getNext(self):
        card = self.cards.pop(0)
        self.updateCount(card)  # Update the count based on the card value
        self.cards.append(card)
        self.shufflePoint += 1
        return card
    
    def updateCount(self, card):
        # Hi-Lo Counting Strategy
        if card.value >= 2 and card.value <= 6:
            self.count += 1
        elif card.value >= 10 or card.value == 11:  # 10, J, Q, K, Ace
            self.count -= 1
    
    def shuffleShoe(self):
        random.shuffle(self.cards)
        self.shufflePoint = 0
        self.count = 0  # Reset the count when the shoe is shuffled

def getBetSize(shoe, balance):
    base_bet = 200  # Base bet of $100
    if shoe.count > 0:
        bet_multiplier = 1 + (shoe.count / 5)
    else:
        bet_multiplier = 1  # Do not decrease bet for negative counts
    
    bet = base_bet * bet_multiplier
    bet = max(bet, base_bet)  # Ensure bet is not below base bet
    return min(bet, balance)  # Ensure bet does not exceed current balance




def hit(hand, shoe):
    hand.addCard(shoe.getNext())

def dealHand(h, dh, s):
    hit(h, s)
    hit(dh, s)
    hit(h, s)
    hit(dh, s)

def dealerPlay(dh, s):
    while (dh.handSum < 17):
        hit(dh, s)

state_size = 270
action_size = 4

Q = np.zeros((state_size, action_size))



def assignState(h, dh):
    current_sum = h.handSum
    dealer_upcard = dh.cards[0].value
    aces = h.ace_count

    return str([current_sum, dealer_upcard, aces])

def determineOutcome(h, dh): #0 is loss, 1 is win, 2 is push
    mySum = h.handSum
    dealerSum = dh.handSum

    if mySum > 21:
        return 0
    elif dealerSum > 21:
        return 1 
    elif mySum < dealerSum: 
        return 0
    elif mySum == dealerSum:
        return 2
    else:
        return 1


def duplicates(lst, item):
    return [i for i, x in enumerate(lst) if x == item]

def actionIndex(options):
    if len(set(options)) == len(options):
        action = np.argmax(options)
    else:
        max_indices = duplicates(options, np.max(options))
        action = np.random.choice(max_indices)
    return action

class Player:
    def __init__(self, balance=1000000):
        self.balance = balance
        self.bet = 0
    
    def placeBet(self, shoe):
        self.bet = getBetSize(shoe, self.balance)  # Get bet size based on count and current balance
        self.balance -= self.bet  # Deduct bet from balance
    
    def updateBalance(self, outcome):
        # Assuming outcome is 0 (loss), 1 (win), 2 (push)
        if outcome == 1:
            self.balance += self.bet * 2  # Win: get back double the bet
        elif outcome == 2:
            self.balance += self.bet  # Push: get back the bet
        # No need to do anything for a loss as the bet is already deducted
