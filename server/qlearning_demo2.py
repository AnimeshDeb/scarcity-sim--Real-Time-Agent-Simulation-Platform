import numpy as np


#step 1: Initial configs

STATES=16
ACTIONS=4

q_table=np.zeros([4,4, ACTIONS])

learning_rate=0.8 #how quickly we pick up new info compared to old
discount_factor=0.9 #how much we care about with immediate vs long term rewards. For maze long term is better
epsilon=1.0 #measures our curiousity, initially at 100%
max_episodes=100 #total runs we do 
reward=0
#step 2: Begin training ai
print("Training the AI: ")

for episode in range(max_episodes):
    state=(0,0) # initial coord of our ai 
    done=False #loop temrination condition

    while not done:
        #choose action
        row,col=state
        if np.random.uniform(0,1)<epsilon:
            action=np.random.randint(0,ACTIONS)# inclusive of first, but exclusive of second params
        else:
            action=np.argmax(q_table[state])
        
        #do action

        #we also ensure that the robot doesn't go outside the grid and use next_row, next_col
        # to avoid manipulating directly row and col because we want to keep a track of
        # 'history' for future runs so ai understands which direction is successful.

        next_row, next_col=row, col
        if action==1:#up
            next_row=max(row-1,0)
        elif action==2:#down
            next_row=min(row+1,3)
        elif action==3:#left
            next_col= max(col-1,0)
        else: #right-> index of 0
            next_col=min(col+1,3)
        
        next_state=(next_row,next_col)

        #apply penalties/rewards

        # we have to do =-10 instead of -=10 because if we do -=10 or +=50, the robot will think
        #that later rounds are more beneficial to start working since it will get more points!
        if next_state==(1,1) or next_state==(1,3) or next_state==(2,3) or next_state==(3,0):
            reward=-10
            done=True 
        elif next_state==(3,3):
            reward=+50
            done=True
        else:
            reward=-1 #This is important! We have to do reward-=1 instead of +=1 or else ai will constantly 
            #be stuck with just moving around, since its getting points
        
        #update q_table
        
        #old_value gets 1 number by retriving a value from a specified column in a row and a specific action in that column, which 
        #corresponds to a singular value
        old_value=q_table[row,col,action]

        #next_max gets the max of 4 numbers. next_state is (next_row, next5_col) and we are effectively just focuysing
        # on retrieving a column in a row and then taking the max of the saiod column.
        next_max=np.max(q_table[next_state])

        new_value=old_value+learning_rate*(reward + discount_factor*next_max-old_value)

        # we are basically replacing the old_value with a better new_value. This is better
        # because it takes into account the learning_rate. It's effectively a score that reflects new information.
        # Essentially we replace the current_value with new_value (which is a reflection of next_state). This
        #tells inn future runs, what is the next spot to go from current state!!

        q_table[row, col, action]=new_value

        #After we finish updating the current cell for future runs, we update the current state to be the next_state.`  `
        state=next_state
    
    if epsilon>0.01:
        epsilon-=0.02

print("TRAINING COMPLETE")
print(q_table)



