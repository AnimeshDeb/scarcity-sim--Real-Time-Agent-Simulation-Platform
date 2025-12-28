import numpy as np



def Agent_logic(num_food,world_dimension, num_episodes):
    

    STATES=36
    ACTIONS=4
    NUM_FOOD=num_food
    FOOD_POSITION=[(0,0)]*NUM_FOOD
    DIMENSION=world_dimension
    HEALTH=100
    print("food position: ", FOOD_POSITION)

    for i in range(len(FOOD_POSITION)):
        first=np.random.randint(1,DIMENSION) #ensuring that food doesn't spawn where ai starts at 
        second=np.random.randint(1, DIMENSION)
        FOOD_POSITION[i]=(first,second)

    q_table=np.zeros([DIMENSION,DIMENSION,ACTIONS])

    learning_rate=0.8
    discount_factor=0.9
    epsilon=1.0
    max_episodes=num_episodes
    reward=0


    print("Training the ai")

    for episode in range(max_episodes):
        state=(0,0)
        done=False 
        current_health=HEALTH
        food_pos=FOOD_POSITION.copy()
        while not done:

            row,col=state 
            if np.random.uniform(0,1)<epsilon:
                action=np.random.randint(0,ACTIONS)
            else:
                action=np.argmax(q_table[state])

            next_row, next_col=row, col

            if action==0:#up
                next_row=max(row-1,0)
            elif action==1:#down
                next_row=min(row+1, DIMENSION-1)
            elif action==2:#left
                next_col=max(col-1, 0)
            else:#right
                next_col=min(DIMENSION-1, col+1)
        
            next_state=(next_row, next_col)
           
            if next_state in food_pos:
                reward=+10
                current_health+=10
                food_pos.remove(next_state) #this is removing food
            elif current_health<=0:
                reward=-100
                done=True 
            else:
                reward=-1
                current_health-=1


            old_value=q_table[row,col,action]

            next_max=np.max(q_table[next_state])


            new_value=old_value+learning_rate*(reward+discount_factor*next_max-old_value)

            q_table[row,col,action]=new_value

            state=next_state 
        if epsilon>0.01:
            epsilon-=0.03
    print("training complete")
    print(q_table)

    #below we basically find the path ai took by iterating through the q_table
    #we also incorporate a new q_table that keeps track of apples that are gone, so ai doesn't continuously loop in ui
    path=[]
    state=(0,0)
    steps=0

    direction_map={0:"up",1:"down", 2:"left", 3:"right"}

    current_health=HEALTH 
    final_food_pos=FOOD_POSITION[:]

    run_q_table=q_table.copy()


    while steps<(DIMENSION*DIMENSION)*2:#if ai takes step into every possible square and then some
        row, col=state 


        best_action_index=np.argmax(run_q_table[row,col])#same as q_table[row][col] but its faster. argmax returns the index value of the largest value
        move_name=direction_map[best_action_index]
        path.append(move_name)

        next_row, next_col=row, col

        if best_action_index==0:
            next_row=max(row-1,0)
        elif best_action_index==1:
            next_row=min(row+1, DIMENSION-1)
        elif best_action_index==2:
            next_col=max(col-1, 0)
        else:
            next_col=min(col+1, DIMENSION-1)
        
        next_state=state=(next_row, next_col)#updating state to consider the next move
        reward=-20
        current_health-=1
       

        if next_state in final_food_pos:
            reward=+100
            current_health+=10
            final_food_pos.remove(next_state)
        elif current_health<=0:
            reward=-100
        
        old_val=run_q_table[row,col,best_action_index]
        next_max=np.max(run_q_table[next_state])
        new_val=old_val+learning_rate*(reward+discount_factor*next_max-old_val)
        run_q_table[row,col,best_action_index]=new_val 
        state=next_state 
        steps+=1

        if row==DIMENSION-1 and col==DIMENSION-1:
            break 

    return {"q_table":q_table.tolist(), "best_path":path, "food_locations":FOOD_POSITION}