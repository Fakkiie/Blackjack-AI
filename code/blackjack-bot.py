from blackjackFunctions import * 
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from Visualize import *


state_size = 260
action_size = 4

Q = np.zeros((state_size, action_size))

no_ace_states = []
ace_states = []

for i in [4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]:
    for j in [2,3,4,5,6,7,8,9,10,11]:
        no_ace_states.append([i,j,0])

for i in [12,13,14,15,16,17,18,19,20]:
    for j in [2,3,4,5,6,7,8,9,10,11]:
        ace_states.append([i,j,1])

all_states = no_ace_states + ace_states

states_dict = {}

for i in np.arange(len(all_states)):
    states_dict[str(all_states[i])] = i

def playGame(rounds, save_path=None):
    s = shoe()
    player = Player()  # Assuming starting balance is set in Player's __init__
    rnd = 0
    epsilon = 0.8
    gamma = 0.35
    record = []
    bets = []  # Track all bets
    outcomes = []  # Track win(1), loss(0), push(2)
    balances = [player.balance]  # Track player balance over time

    while rnd < rounds:
        if rnd % (rounds // 90) == 0:
            epsilon *= 0.9
            print(f"{rnd} rounds done", end='\r')
        if s.shufflePoint < 234:
            bet, result = playRound(s, epsilon, gamma)
            record.append(result)
            bets.append(bet)  # Store the bet size
        else:
            s.shuffleShoe()
            bet, result = playRound(s, epsilon, gamma)
            record.append(result)
            bets.append(bet)  # Store the bet size
        rnd += 1
        
    
    if save_path is not None:
        np.save(save_path, Q)  # Save the Q-table to the specified path
        print(f"Q-table saved to {save_path}")

    return bets

def playRound(s, epsilon, gamma):
    h = hand()
    dh = hand()
    reward = 10  # Base reward
    
    # Adjust the bet based on the card count
    # For simplicity, let's just double the reward if the count is positive
    if s.count > 0:
        reward *= 2  # Double the bet if the count is positive

    queue = []
    dealHand(h, dh, s)
    surrender = False

    while h.handSum < 21:
        state = assignState(h, dh)
        curr_action = chooseAction(state, Q, epsilon)
        queue.append([state, curr_action])
        
        if curr_action == 0:    #hit
            hit(h, s)
        elif curr_action == 1:  #stand
            break
        elif curr_action == 2:  #double
            reward *= 2
            hit(h, s)
            break
        elif curr_action == 3:  #surrender
            surrender = True
            reward = reward / 2  # Lose half the bet on surrender
            break
    
    dealerPlay(dh, s)
    if surrender == True:
        result = 0
    else:
        result = determineOutcome(h, dh)
    
    if result == 0:     #loss
        reward *= -1
    elif result == 2:   #push
        reward = 0
        
    updateQ(queue, reward, gamma)
    return reward, result

def updateQ(queue, reward, gamma):
    i = 0
    lr = 0.0005
    while queue:
        curr = queue.pop()
        curr_state = curr[0]
        curr_action = curr[1]

        rowNum = states_dict[curr_state]
        
        Q[rowNum][curr_action] += lr * (reward * (gamma ** i))
        i += 2
        

def chooseAction(state, Q, epsilon):
    value = np.random.choice(a = np.arange(0, 2), p = [1-epsilon, epsilon])
    if value == 1:  #random choice epsilon percent of the time
        action = random.choice([0,1,2,3])
    else:   #choose best option from q table 1-epsilon percent of the time
        options = Q[states_dict[state]]
        action = actionIndex(options)   
    return action

def whatAction(lst):
    action = np.argmax(lst)
    if action == 0:
        print("hit")
    elif action == 1:
        print("stay")
    elif action == 2:
        print("double")
    elif action == 3:
        print("surrender")
    print(lst)


bets = playGame(10000000, save_path="Q_table.npy")
minimum_bet = min(bets)
average_bet = sum(bets) / len(bets)
maximum_bet = max(bets)

print("Minimum bet size:", minimum_bet)
print("Average bet size:", average_bet)
print("Maximum bet size:", maximum_bet)

#Generate Tables/Graphs and display them
basic_strategy = pd.DataFrame(columns=dealer_upcard, index=no_ace_hand + ace_hand) 
Q_loaded = np.load("Q_table.npy")
generateBS(Q_loaded, basic_strategy, 'within 0.5%')  
visualize_basic_strategy(basic_strategy)
visualize_bets(bets)