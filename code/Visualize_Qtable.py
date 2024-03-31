from blackjackFunctions import * 
import numpy as np
import pandas as pd
from Visualize import *

Q_play = np.load("Q_table.npy")

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

def playGame_visualize():
    s = shoe()
    player = Player()  # Assuming starting balance is set in Player's __init__
    rnd = 0
    s.running_count += 15

    print("Playing Game:")
    print("---------------------")
    while rnd < 10: #and player.balance > 0:
        print(f"Round {rnd+1}")
        bet, reward, result = playRound_visualize(s, player)
        print(f"Result: {result} (0: loss, 1: win, 2: push)")
        player.balance += reward
        print(f"Player Bet: {bet}")
        print(f"Player won/lost: {reward}")
        print(f"New Balance: {player.balance}")
        rnd += 1

def playRound_visualize(s: shoe, player: Player):
    h = hand()
    dh = hand()
    
    bet = 10
    dealHand(h, dh, s)
    surrender = False
    reward = bet

    print(f"\tTrue Count: {s.true_count}")

    while h.handSum < 21:
        state = assignState(h, dh)
        curr_action = chooseAction(state, Q_play)
        print(f"\tHand: {h.handSum}")
        print(f"\tDealer Showing: {dh.handSum}")
        print(f"\tAction: {curr_action} (0: hit, 1: stand, 2: double, 3: surrender)")

        
        if curr_action == 0:    #hit
            hit(h, s)
            print(f"\tNew Hand: {h.handSum}")
        elif curr_action == 1:  #stand
            break
        elif curr_action == 2:  #double
            reward *= 2
            hit(h, s)
            print(f"\tNew Hand: {h.handSum}")
            break
        elif curr_action == 3:  #surrender
            surrender = True
            reward *= 0.5 
            break
        
    dealerPlay(dh, s)
    print(f"\tDealer Hand: {dh.handSum}")
    if surrender == True:
        result = 0
    else:
        result = determineOutcome(h, dh)
    
    if result == 0:     #loss
        reward *= -1 
    elif result == 2:   #push
        reward = 0
    
    return bet, reward, result

def chooseAction(state, Q):
    options = Q[states_dict[state]]
    action = actionIndex(options)   
    return action

# Play 10 rounds
playGame_visualize()

# Generate Tables/Graphs and display them
basic_strategy = pd.DataFrame(columns=dealer_upcard, index=no_ace_hand + ace_hand) 
Q_loaded = np.load("Q_table.npy")
generateBS(Q_loaded, basic_strategy, 'None')    # second action, within 0.5%, None
visualize_basic_strategy(basic_strategy)