import random
from enum import Enum

#Defines the ranks associated with each card
ranks = {
    "2" : 2,
    "3" : 3,
    "4" : 4,
    "5" : 5,
    "6" : 6,
    "7" : 7,
    "8" : 8,
    "9" : 9,
    "10" : 10,
    "J" : 10,
    "Q" : 10,
    "K" : 10,
    "A" : (1,11)
}

#Defines the Suits as an enum
class Suit(Enum):
    spades = "spades",
    clubs = "clubs",
    diamonds = "diamonds",
    hearts = "hearts"

#Defines the card class for a single card
class Card:
    #Initilizes suit, rank, and value of card for logic
    def init(self, suit, rank, value):
        self.suit = suit
        self.rank = rank
        self.value = value
    
    #Returns the card as a string representation
    def cardType(self):
        return self.rank + " of " + self.suit.value

#Defines the deck class to represent 6 decks of cards
class Deck:
    def init(self,numDecks = 6):
        self.cards = [] #Initialize an empty list to hold cards

        #Create the specified number of decks and add them to the card list
        for i in range(numDecks):
            for suit in Suit:
                for rank, value in ranks.items():
                    self.cards.append(Card(suit, rank, value))
        self.Shuffle()  #Shuffle the deck once it has been made

    #Shuffles the deck using random.
    def Shuffle(self):
        random.shuffle(self.cards)

    #Deal a card by removing and returning the first card from the deck
    #If the deck is empty, return None
    def Deal(self):
        if len(self.cards > 0):
            return self.cards.pop(0)
        else:
            return None  #Empty Deck Case
        
    def Peek(self):
        if len(self.cards) > 0:
            return self.cards[0]
        return None
    #Need to implement add card to bottom, string representation of the deck, and len of deck for game logic
