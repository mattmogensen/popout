
import sys
import numpy as np
import random
import numpy.random
import matplotlib.pyplot as plt
import matplotlib.figure
import time


def display_board(state, winning,board_height,board_length):
    #this function displays the graphics
    plt.show()
    fig, ax = plt.subplots()
    ax.cla()
    ax.set_xlim((0, board_length + 1))
    ax.set_ylim((0, board_height + 1))
    my_ticks = list(range(board_length+1))
    del my_ticks[0]
    plt.xticks(my_ticks)
    ax.get_yaxis().set_visible(False)
    fig.patch.set_facecolor('xkcd:light blue')
    
    human_color = '#A50808'
    computer_color = '#F4BC1C'
    
    for i in range(board_height):
        for j in range(board_length):
            if state[i][j] == 1: 
                plt.gcf().gca().add_artist(plt.Circle((j+1,board_height-i), 0.4, color=human_color, fill=True))
                plt.gcf().gca().add_artist(plt.Circle((j+1,board_height-i), 0.4, color='black', fill=False))
            elif state[i][j] == -1:
                plt.gcf().gca().add_artist(plt.Circle((j+1,board_height-i), 0.4, color=computer_color, fill=True))
                plt.gcf().gca().add_artist(plt.Circle((j+1,board_height-i), 0.4, color='black', fill=False))

    if winning == 1:
        plt.text(0.25,board_height, 'Congratulations you have won!', fontsize=20)
    elif winning == -1:
        plt.text(1,board_height, '   Sorry you have lost!', fontsize=20)
    elif winning == -2:
        plt.text(1,board_height, '   The game is a tie', fontsize=20)


def local_reward(score):
    #translates a raw score fron the board into a value
    #LOCAL reward function, NOT a global reward function
    #currently not implemented in the main(), might be used for final baseline
    
    #One weakness of this local reward function, where
    #we are giving a aligned sequences that we can create by playing in each slot, 
    #as opposed to a global reward function where we might consider the state of the entire board
    #An example of this weakness is that an opponent could possibly stack pieces on either side of 
    #a column and force a win 
    #later in the game
    
    if score == 4: #first choice: do the win
        return 100000
    elif score == 31: #2nd choice: block a win
        return 1000
    elif score == 21: #3rd choice: place chip next to two lone opponent chips
        return 100
    elif score == 22: #sandwich two opponent chips
        return 10
    elif score == 13 or score == 3: #line up 3
        return 1
    elif score == 2: #line up 2
        return 0.1
    else:
        return 0

def generate_copy(state, board_height, board_length):
    #makes a copy to avoid Python creasting a pointer
    new_state = np.zeros((board_height, board_length))
    for i in range(board_height):
        for j in range(board_length):
            new_state[i][j] = state[i][j]
    return new_state

def check_win(state, player, board_height, board_length):
    #returns player if the board state contains a player win
    #returns -player if the board state contains a -player win
    #otherwise returns 0
    
    #check horizontal victory
    for i in range(board_height):
        for j in range(board_length-3):
            score = sum(state[i][j+k] for k in range(4))
            if score == 4*player:
                return player
            elif score == -4*player:
                return -player
    
    #check vertical victory
    for i in range(board_height-3):
        for j in range(board_length):
            score = sum(state[i+k][j] for k in range(4))
            if score == 4*player:
                return player
            elif score == -4*player:
                return -player
            
    #check backward diagonal victory
    for i in range(board_height - 3):
        for j in range(board_length - 3):
            score = sum(state[i+k][j+k] for k in range(4))
            if score == 4*player:
                return player
            elif score == -4*player:
                return -player

    #check forward diagonal victory
    for i in range(board_height - 3):
        for j in range(3,board_length):
            score = sum(state[i+k][j-k] for k in range(4))
            if score == 4*player:
                return player
            elif score == -4*player:
                return -player
                
    return 0
    

def reward(state,player):
    #Given a board state, and an action that is to be played by 'player',
    #return the expected immediate reward
   
    if check_win(state, player):
        return 1000
    else:
        return 0

        
def height(state,slot, board_height, board_length):
    #returns the height of a chip to be played, given the slot
    for i in range(0,board_height):
        if state[board_height-1-i][slot] == 0:
            return board_height-1-i
    #return illegal move
    return float('-inf')
             
#generates a list of feasible actions
def feasible_actions(state, player, board_height, board_length):
    actions = []
    #addition slots
    for slot in range(board_length):
        if state[0][slot] == 0:
            actions.append(slot)
    
    #popout slots
    for slot in range(board_length):
        if state[board_height - 1][slot] == player:
            actions.append(slot+0.5)
            
    return actions

#update board state space with an action
def do_action(state,action,player, board_height, board_length):

    if round(action) == action: #if we are adding a chip
        #place chip   
        state[height(state,action,board_height, board_length)][action] = player
    else:
        #popout chip
        #print('we are popping out')
        #print(action)
        slot = int((action - 0.5))
        #print('decreasing slot ' + str(slot))
        for i in range(board_height):
            #shift chips down
            a = state[board_height-2-i][slot]
            state[board_height-1-i][slot] = a
        state[0][slot] = 0
         
    return state
     
#returns true if the board is full and it's a tie
def tie(state, board_height, board_length):
    check = 0
    for i in range(board_height):
        for j in range(board_length):
            if state[i][j] == 0:
                check += 1
    if check == 0:
        return True
    else:
        return False
    
def get_human_action(state, board_height, board_length):
    feasible = False
    human = 1
    actions = feasible_actions(state, human, board_height, board_length)
    
    #print(actions)
    #print(state)
    
    while not feasible:     
        m = input('Enter your move, red player: \n')
        move = int(m)
        if (move-1 in actions) or (-move - 0.5 in actions):
            feasible = True
    
    if move > 0:
        #print('human has played ' + str(move-1))
        return move - 1
    else:
        #print('human has popped out ' + str(-move - 0.5))
        return -move - 0.5

def get_random_action(state, actions, board_height, board_length):
    #returns an AI action chosen uniformly at random
    AI = -1

    if actions == []:
        print('Game is a tie.')
        sys.exit()
        
    actions = feasible_actions(state,AI, board_height, board_length)
    
    return random.choice(actions)


def get_minimax_action(state,depth, board_height, board_length, discount):
    
    def minimax(state,player,Depth, board_height, board_length, discount):
        #print('current depth is ' + str(Depth))
        #print('current player is ' + str(player))
        #returns the minimax value for a given agent
        win_state = check_win(state, player, board_height, board_length)
        if win_state == player and player == -1:
            return 100
        elif win_state == player and player == 1:
            return -100
        elif Depth <= 0:
            return 0
        elif player == -1: #AI player, maximize score
            return discount * maxOverActions(state,player,Depth, board_height, board_length)[0]
        else: #human player, minimize score
            return discount * minOverActions(state,player,Depth, board_height, board_length)[0]
        
    def maxOverActions(state,player,Depth, board_height, board_length):
        #returns the (value,action) pair that maximizes the score for the AI
        actions = feasible_actions(state,player, board_height, board_length)
        best = (float('-inf'), random.choice(actions))
        for action in random.sample(actions,len(actions)):
            next_state = do_action(generate_copy(state, board_height, board_length),action,player, board_height, board_length)
            next_value = minimax(next_state,-player,Depth, board_height, board_length, discount)
            if next_value > best[0]:
                best = (next_value, action)
        #print('best AI play is : ' + str(best))
        return best
    
    def minOverActions(state,player,Depth, board_height, board_length):
        #returns the (value,action) pair that minimizes the score for the human
        actions = feasible_actions(state,player, board_height, board_length)
        best = (float("inf"), random.choice(actions))
        for action in random.sample(actions,len(actions)):
            next_state = do_action(generate_copy(state, board_height, board_length),action,player, board_height, board_length)
            next_value = minimax(next_state,-player,Depth-1, board_height, board_length, discount)
            if next_value < best[0]:
                best = (next_value, action)
        #print('best human play is : ' + str(best))
        return best
    
    a = maxOverActions(state, -1, depth,  board_height, board_length)
    #print('we are returning ' + str(a))
    return a[1]
    # END_YOUR_CODE
    
    
def display_intro(board_height, board_length, strategy):
    #generates an intro screen

    state = [[-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],\
             [-1, 1, 1, 1,-1, 1, 1, 1,-1, 1, 1, 1,-1,-1,-1,-1,-1,-1,-1],\
             [-1, 1,-1, 1,-1, 1,-1, 1,-1, 1,-1, 1,-1,-1,-1,-1,-1,-1,-1],\
             [-1, 1, 1, 1,-1, 1,-1, 1,-1, 1, 1, 1,-1,-1,-1,-1,-1,-1,-1],\
             [-1, 1,-1,-1,-1, 1,-1, 1,-1, 1,-1,-1,-1,-1,-1,-1,-1,-1,-1],\
             [-1, 1,-1,-1,-1, 1, 1, 1,-1, 1,-1,-1,-1,-1,-1,-1,-1,-1,-1],\
             [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1],\
             [-1,-1,-1,-1,-1,-1,-1, 1, 1, 1,-1, 1,-1, 1,-1, 1, 1, 1,-1],\
             [-1,-1,-1,-1,-1,-1,-1, 1,-1, 1,-1, 1,-1, 1,-1,-1, 1,-1,-1],\
             [-1,-1,-1,-1,-1,-1,-1, 1,-1, 1,-1, 1,-1, 1,-1,-1, 1,-1,-1],\
             [-1,-1,-1,-1,-1,-1,-1, 1,-1, 1,-1, 1,-1, 1,-1,-1, 1,-1,-1],\
             [-1,-1,-1,-1,-1,-1,-1, 1, 1, 1,-1, 1, 1, 1,-1,-1, 1,-1,-1],\
             [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]] 
                 
    print('Welcome to the game of Popout where the first player to align 4 chips wins the game.')
    print('Enter a positive integer followed by ENTER to play your chip in a given slot.')
    print('Enter the same number as a NEGATIVE integer followed by ENTER to pop out your bottom chip from a given slot.')
    print(' ')
    print('Human player is red and goes first')
    print('AI opponent is using a ' + strategy + ' strategy.')
    fig, ax = plt.subplots()
    display_board(state, 0, 13, 19)
    plt.show()
    input('- Press ENTER button to continue -')
    
    matplotlib.figure.Figure.clear(fig, ax)
    display_board(np.zeros((board_height,board_length)),0,board_height, board_length)
    plt.show()
        
def main():
    
    human = 1
    AI = -1
    depth = 3
    strategy = 'minimax'
    discount = 0.95
    board_length = 7
    board_height = 5
    fig, ax = plt.subplots() 
    display_intro(board_length,board_height, strategy)
    matplotlib.figure.Figure.clear(fig, ax)
    state = np.zeros((board_height, board_length))
    display_board(state, 0, board_height, board_length)
    plt.show()
    
    end_game = False
    while end_game is False:
        
        plt.show()
        
        state = do_action(generate_copy(state, board_height, board_length),\
                          get_human_action(state, board_height, board_length),\
                              human, board_height, board_length)

        win_state = check_win(state, AI, board_height, board_length)
        print(' ')
        if win_state == -1:
            print('Sorry, the computer has won.')
            display_board(state, -1, board_height, board_length)
            plt.show()
            sys.exit
        
        elif win_state == 1:
            print('Congratulations, you have won!!')
            display_board(state, 1, board_height, board_length)
            plt.show()
            sys.exit()

        elif tie(state, board_height, board_length):
            print('The game is a tie.')
            winning = -2
            display_board(state, -2, board_height, board_length)
            plt.show()
            sys.exit()
            
        else:
            display_board(state, 0, board_height, board_length)
            plt.show()
 
        if strategy == 'minimax':
            state = do_action(generate_copy(state, board_height, board_length),\
                          get_minimax_action(state,depth, board_height, board_length, discount),\
                              AI, board_height, board_length)
        else:
            state = do_action(generate_copy(state, board_height, board_length),\
                          get_random_action(state,depth, board_height, board_length),\
                              AI, board_height, board_length)
    
        win_state = check_win(state, AI, board_height, board_length)
    
        if win_state == -1:
            print('Sorry, the computer has won.')
            display_board(state, -1, board_height, board_length)
            plt.show()
            sys.exit
            
        elif win_state == 1:
            print('Congratulations, you have won!!')
            display_board(state, 1, board_height, board_length)
            plt.show()
            sys.exit

        elif tie(state, board_height, board_length):
            print('The game is a tie.')
            display_board(state, -2, board_height, board_length)
            plt.show()
            sys.exit()
            
        else:             
            display_board(state,  0, board_height, board_length)
            plt.show()
            

main()

