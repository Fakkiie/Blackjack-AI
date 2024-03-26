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

def playGame(rounds, save_path):
    s = shoe()
    player = Player()  # Assuming starting balance is set in Player's __init__
    rnd = 0
    epsilon = 0.8 #0.8
    gamma = 0.35 #0.35
    record = []
    bets = []  # Track all bets
    balances = []  # Track player balance over time

    while rnd < rounds: #and player.balance > 0:
        if rnd % (rounds // 90) == 0:
            epsilon *= 0.90
            print(f"{rnd} rounds done", end='\r')
        if s.shufflePoint < 234:
            bet, reward, result = playRound(s, player, epsilon, gamma)
            player.balance += reward
            if rnd >= rounds-10000:
                if result == 2:
                    record.append(0.5)
                elif result != 3:
                    record.append(result)
            balances.append(player.balance)
            bets.append(bet)  # Store the bet size
        else:
            s.shuffleShoe()
            bet, reward, result = playRound(s, player, epsilon, gamma)
            player.balance += reward
            if rnd >= rounds-10000:
                if result == 2:
                    record.append(0.5)
                elif result != 3:
                    record.append(result)
            balances.append(player.balance) 
            bets.append(bet)  # Store the bet size
        rnd += 1
        
    
    if save_path is not None:
        np.save(save_path, Q)  # Save the Q-table to the specified path
        print(f"Q-table saved to {save_path}")

    return bets, balances, record

def playRound(s: shoe, player: Player, epsilon, gamma):
    h = hand()
    dh = hand()
    
    bet = 10
    queue = []
    dealHand(h, dh, s)
    surrender = False
    reward = bet

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
            reward *= 1  # Lose half the bet on surrender
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


    return bet, reward, result

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


[bets, balance_history, record] = playGame(9000000, save_path="Q_table.npy")
minimum_bet = min(bets)
average_bet = sum(bets) / len(bets)
maximum_bet = max(bets)
winrate = sum(record) / len(record)

print("Minimum bet size:", minimum_bet)
print("Average bet size:", average_bet)
print("Maximum bet size:", maximum_bet)
print("Winrate:", winrate)
print("Ending balance:", balance_history[-1])

#Generate Tables/Graphs and display them
basic_strategy = pd.DataFrame(columns=dealer_upcard, index=no_ace_hand + ace_hand) 
Q_loaded = np.load("Q_table.npy")
generateBS(Q_loaded, basic_strategy, 'None')  
visualize_basic_strategy(basic_strategy)
# visualize_bets(bets)
visualize_balance(balance_history)