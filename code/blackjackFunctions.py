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
    
    def printHand(self):
        return self.handSum
        
        
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
        self.cardsDelt = 0
        self.decksDelt = 0
        self.running_count = 0 
        self.true_count = 0
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
        self.cardsDelt += 1
        self.shufflePoint += 1

        if self.cardsDelt % 52 == 0:
            self.decksDelt += 1

        return card
    
    def updateCount(self, card: card):
        # Hi-Lo Counting Strategy
        if card.value >= 2 and card.value <= 6:
            self.running_count += 1
        elif card.value >= 10:  # 10, J, Q, K, Ace
            self.running_count -= 1
        self.true_count = self.running_count // (6 - self.decksDelt)
    
    def shuffleShoe(self):
        random.shuffle(self.cards)
        self.shufflePoint = 0
        self.running_count = 0  # Reset the count when the shoe is shuffled
        self.cardsDelt = 0
        self.decksDelt = 0

def getBetSize(shoe: shoe, balance):
    base_bet = 10 # Min bet of $10
    
    if shoe.true_count >= 10:
        bet_multiplier = 50 + (shoe.true_count)
    elif shoe.true_count >= 5:
        bet_multiplier = 25 + (shoe.true_count)
    elif shoe.true_count >= 2:
        bet_multiplier = 1 + (shoe.true_count)
    else: 
        bet_multiplier = 1
    
    bet = base_bet * bet_multiplier
    #bet = max(bet, base_bet)  # Ensure bet is not below base bet
    return bet #min(bet, balance)  # Ensure bet does not exceed current balance

def hit(hand: hand, shoe: shoe):
    hand.addCard(shoe.getNext())

def dealHand(h, dh, s):
    hit(h, s)
    hit(dh, s)
    hit(h, s)
    hit(dh, s)

def dealerPlay(dh: hand, s: shoe):
    while (dh.handSum < 17):
        hit(dh, s)

state_size = 270
action_size = 4

Q = np.zeros((state_size, action_size))



def assignState(h: hand, dh: hand):
    current_sum = h.handSum
    dealer_upcard = dh.cards[0].value
    aces = h.ace_count

    return str([current_sum, dealer_upcard, aces])

def determineOutcome(h: hand, dh: hand): #0 is loss, 1 is win, 2 is push
    mySum = h.handSum
    dealerSum = dh.handSum

    if mySum == 21:
        return 1
    elif mySum > 21:
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
    def __init__(self, balance=100000):
        self.balance = balance
        self.bet = 0
    
    def placeBet(self, shoe):
        self.bet = getBetSize(shoe, self.balance)  # Get bet size based on count and current balance
        # self.balance -= self.bet  # Deduct bet from balance
