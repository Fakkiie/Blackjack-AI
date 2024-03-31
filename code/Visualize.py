import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import heapq
import ast
from matplotlib.colors import ListedColormap

def visualize_basic_strategy(basic_strategy):
    # Map actions to numerical values for coloring
    action_map = {'Hit': 0, 'Hit (c)': 0, 'Stand': 1, 'Stand (c)': 1, 'Double': 2, 'Surrender': 3,
                  'Double (c)': 2, 'Surrender (c)': 3}
    # Replace actions with their corresponding numerical values
    temp_df = basic_strategy.replace(action_map)

    # Define custom colors for each action, according to your specific color requirements
    custom_colors = ['green', 'red', 'blue', 'yellow']  # Adjusted color mapping based on your specifications
    cmap = ListedColormap(custom_colors)

    # Create the heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(temp_df, annot=basic_strategy, fmt='', cmap=cmap, cbar=False, linewidths=.5)
    plt.title('Basic Strategy Heatmap')
    plt.xlabel('Dealer Showing')
    plt.ylabel('Player Hand')
    plt.show()

def visualize_bets(bets):
    fig, ax = plt.subplots(2, 1, figsize=(10, 8))

    # Histogram of bet sizes
    ax[0].hist(bets, bins=30, color='skyblue', edgecolor='black')
    ax[0].set_title('Distribution of Bet Sizes')
    ax[0].set_xlabel('Bet Size')
    ax[0].set_ylabel('Frequency')

    # Line plot of bet sizes over time
    ax[1].plot(bets, color='darkblue')
    ax[1].set_title('Bet Sizes Over Rounds')
    ax[1].set_xlabel('Round')
    ax[1].set_ylabel('Bet Size')

    plt.tight_layout()
    plt.show()

def visualize_balance(balance_history):
    plt.figure(figsize=(10, 6))
    plt.plot(balance_history, color='blue')
    plt.title('Bot Balance Over Rounds')
    plt.xlabel('Round')
    plt.ylabel('Balance')
    plt.grid(True)
    plt.show()


def percentChange(current, previous): #returns percent change between current and previous
    if current == previous:
        return 0
    try:
        return (abs(current - previous) / previous) * 100.0
    except ZeroDivisionError:
        return float('inf')
    
#-----------------------#given a row in the Q table, returns action that the model believes is best (max)------------------------------------------------
def whichAction(row): 
    action = np.argmax(row)
    if action == 0:
        return 'Hit'
    elif action == 1:
        return 'Stand'
    elif action == 2:
        return 'Double'
    elif action == 3:
        return "Surrender"

#-----------------------nth best action according to the model within percent% of max action------------------------------------------------
def nextAction(row, n, percent = 0):
    if n > 4: #only 4 possible actions
        return "Error, only 4 actions are possible (n>4)"
    
    action = heapq.nlargest(n, range(len(row)), key = row.__getitem__)[n-1] #index of nth max
    action_val = heapq.nlargest(n, row)[1] #value of nth max
    
    if percent: #if we want to check that the nth action is within percent% of the max action
        if percentChange(action_val, np.max(row)) > percent: 
            return "No"
        
    if action == 0:
        return 'Hit (c)'
    elif action == 1:
        return 'Stand (c)'
    elif action == 2:
        return 'Double (c)'
    elif action == 3 and n == 2:
        return "Surrender"
    elif action == 3 and n == 3:
        return "Surrender (c)"
    
#-----------------------highlight cells with color according to action------------------------------------------------
def highlight_actions(val):
    if val == 'Hit':
        color = 'green'
    elif val == 'Stand':
        color = 'brown'
    elif val == 'Double':
        color = 'blue'
    elif val == 'Surrender':
        color = 'goldenrod'
    elif val == 'Hit (c)':
        color = 'darkgreen'
    elif val == 'Stand (c)':
        color = 'firebrick'
    elif val == 'Double (c)':
        color = 'mediumblue'
    elif val == 'Surrender (c)':
        color = 'darkgoldenrod'
    else:
        color = 'white'
    return 'background-color: %s' % color

#-------------------given a state in Q table, returns [row, column] coordinates in basic_strategy table----------------
def state_to_BS(state): 
    state_lst = ast.literal_eval(state)
    hand_total = state_lst[0]
    dealer_upcard = state_lst[1]
    if dealer_upcard == 11:
        dealer_upcard = 'A'
        
    ace = state_lst[2]
    
    BS_column = dealer_upcard
    
    if ace:
        if hand_total == 12:
            hand_total = 'A,A'
        else:
            hand_total = 'A,%i'%(hand_total-11)
    
    BS_row = hand_total  
    
    return [BS_row, BS_column]

#-------------------generate dictionary with keys = row number in Q, and value = corresponding state-----------------
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
    states_dict[i] = str(all_states[i])

#-------------------generates basic strategy table according to Q and with any corrections desired-----------------
    
def generateBS(Q, basic_strategy, correction):
    for num, row in enumerate(Q):
        state = states_dict[num]
        action = whichAction(row)
        bs_coords = state_to_BS(state)
        
        if correction != 'None':
            if correction == 'within 0.5%':
                p = 0.005
            elif correction == 'second action':
                p = 0
                
            if action != correct_bs.loc[bs_coords[0], bs_coords[1]]:
                #either just the next action ('second action') or next action within p% ('within 0.5%')
                second_action = nextAction(row, 2, p)
                if second_action != "No":
                    action = second_action

            if action == "Surrender" and action != correct_bs.loc[bs_coords[0], bs_coords[1]]:
                action = nextAction(row, 3)
        
        basic_strategy.loc[bs_coords[0], bs_coords[1]] = action
    return basic_strategy.style.applymap(highlight_actions)


#empty basic_strategy to fill with Q table
# Example definitions (ensure these reflect your actual code)
dealer_upcard = [2,3,4,5,6,7,8,9,10,'A']
no_ace_hand = [4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
ace_hand = ['A,A', 'A,2', 'A,3', 'A,4', 'A,5', 'A,6', 'A,7', 'A,8', 'A,9']
basic_strategy = pd.DataFrame(columns=dealer_upcard, index=no_ace_hand)
basic_strategy_ace = pd.DataFrame(columns=dealer_upcard, index=ace_hand)
# Append basic_strategy_ace to basic_strategy
basic_strategy = pd.concat([basic_strategy, basic_strategy_ace], ignore_index=False)

#generate table with correct basic strategy

dealer_upcard = [2,3,4,5,6,7,8,9,10,'A']
no_ace_hand = [4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
ace_hand = ['A,A', 'A,2', 'A,3', 'A,4', 'A,5', 'A,6', 'A,7', 'A,8', 'A,9']
basic_strategy = pd.DataFrame(columns = dealer_upcard, index = no_ace_hand)
basic_strategy_ace = pd.DataFrame(columns = dealer_upcard, index = ace_hand)
correct_bs = pd.concat([basic_strategy, basic_strategy_ace], axis=0)


correct_bs.loc[4] = "Hit"
correct_bs.loc[5] = "Hit"
correct_bs.loc[6] = "Hit"
correct_bs.loc[7] = "Hit"
correct_bs.loc[8] = "Hit"
correct_bs.loc[9] = ["Hit", "Double", "Double", "Double", "Double", "Hit", "Hit", "Hit", "Hit", "Hit"]
correct_bs.loc[10] = ["Double","Double","Double","Double","Double","Double","Double","Double","Hit", "Hit"]
correct_bs.loc[11] = "Double"
correct_bs.loc[12] = ["Hit", "Hit", "Stand", "Stand", "Stand", "Hit","Hit","Hit","Hit","Hit"]
correct_bs.loc[13] = ["Stand","Stand","Stand","Stand","Stand","Hit","Hit","Hit","Hit","Hit"]
correct_bs.loc[14] = ["Stand","Stand","Stand","Stand","Stand","Hit","Hit","Hit","Hit","Hit"]
correct_bs.loc[15] = ["Stand","Stand","Stand","Stand","Stand","Hit","Hit","Hit","Surrender","Surrender"]
correct_bs.loc[16] = ["Stand","Stand","Stand","Stand","Stand","Hit","Hit","Surrender","Surrender","Surrender"]
correct_bs.loc[17] = "Stand"
correct_bs.loc[18] = "Stand"
correct_bs.loc[19] = "Stand"
correct_bs.loc[20] = "Stand"
correct_bs.loc['A,A'] = ["Hit", "Hit", "Stand", "Stand", "Stand", "Hit","Hit","Hit","Hit","Hit"]
correct_bs.loc['A,2'] = ["Hit", "Hit", "Hit", "Double", "Double", "Hit","Hit","Hit","Hit","Hit"]
correct_bs.loc['A,3'] = ["Hit", "Hit", "Hit", "Double", "Double", "Hit","Hit","Hit","Hit","Hit"]
correct_bs.loc['A,4'] = ["Hit", "Hit", "Double", "Double", "Double", "Hit","Hit","Hit","Hit","Hit"]
correct_bs.loc['A,5'] = ["Hit", "Hit", "Double", "Double", "Double", "Hit","Hit","Hit","Hit","Hit"]
correct_bs.loc['A,6'] = ["Hit", "Double", "Double", "Double", "Double", "Hit","Hit","Hit","Hit","Hit"]
correct_bs.loc['A,7'] = ["Double", "Double", "Double", "Double", "Double", "Stand","Stand","Hit","Hit","Hit"]
correct_bs.loc['A,8'] = ["Stand", "Stand", "Stand", "Stand", "Double", "Stand","Stand","Stand","Stand","Stand"]
correct_bs.loc['A,9'] = "Stand"
correct_bs.style.applymap(highlight_actions)

# #dictionary of 22 tested Q tables
# QTables = {}
# for i in range(1, 23):  # Assuming you have 22 Q-tables
#     path = "/Users/ethan/Documents/Projects/Blackjack_bot/Blackjack-AI/data/QTables/Q_table-%i.npy" % i
#     QTables[i] = np.load(path)


# generateBS(QTables[19], basic_strategy)
# #empty corrected basic strategy data frame to fill
# basic_strategy_corrected = pd.DataFrame(columns = dealer_upcard, index = no_ace_hand)
# basic_strategy_ace = pd.DataFrame(columns = dealer_upcard, index = ace_hand)
# basic_strategy_corrected = pd.concat([basic_strategy_corrected, basic_strategy_ace], axis=0)


# generateBS(QTables[19], basic_strategy_corrected,'within 0.5%')
# generateBS(QTables[19], basic_strategy_corrected, 'second action')

reverse_states_dict = {}

for i in np.arange(len(all_states)):
    reverse_states_dict[str(all_states[i])] = i
