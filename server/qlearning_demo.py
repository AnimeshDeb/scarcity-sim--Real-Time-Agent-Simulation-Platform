import numpy as np
import time

# --- SETUP THE ENVIRONMENT ---
# 6 States (Spots 0-5)
# 2 Actions (0=Left, 1=Right)
STATES = 6
ACTIONS = 2

# Initialize the Q-Table with zeros
# Rows = States, Columns = Actions
q_table = np.zeros((STATES, ACTIONS))

# --- HYPERPARAMETERS (The AI's Personality) ---
learning_rate = 0.8     # How fast we update our old beliefs (Alpha)
discount_factor = 0.9   # How much we care about future rewards vs immediate ones (Gamma)
epsilon = 1.0           # Exploration rate: 100% random at start
max_episodes = 100       # How many times we play the game to train

# --- THE TRAINING LOOP ---
print("Training the AI...")

for episode in range(max_episodes):
    state = 0   # Always start at spot 0
    done = False
    
    while not done:
        # 1. CHOOSE ACTION (Exploration vs Exploitation)

        #basically choosing a random number between 0,1 and then seeing if that's less
        # than the curiosity threshold, if it's less than threshold, it explores since it's very
        # curious. If its more than threshold, it will check the q_table, since its not as curious.
        if np.random.uniform(0, 1) < epsilon:
            action = np.random.randint(0, ACTIONS) # Explore: Random move
        else:
            action = np.argmax(q_table[state])     # Exploit: Best known move

        # 2. PERFORM ACTION (Simulate the Environment)
        # Logic: If action is 0 move left, if 1 move right. Clamp between 0-5.
        if action == 1: # Moving Right
            next_state = state + 1
        else:           # Moving Left
            next_state = state - 1
            
        # Keep agent within bounds (can't go below 0 or above 5)
        next_state = max(0, min(next_state, STATES - 1))

        # 3. GET REWARD (The Feedback)
        if next_state == 5:     # Reached Goal (Fridge)
            reward = 10
            done = True
        else:
            reward = -1         # Small penalty to encourage speed

        # 4. UPDATE Q-TABLE (The Bellman Equation)
        # Old Q-value for the current state/action
        old_value = q_table[state, action]
        
        # What is the BEST possible score from the NEXT state?
        next_max = np.max(q_table[next_state])
        
        # Calculate the new value. Thhis is error correction/ bellman equation
        new_value = old_value + learning_rate * (reward + discount_factor * next_max - old_value)
        
        # Write it into the table
        q_table[state, action] = new_value

        # Move to the next state
        state = next_state

    # Decay Epsilon (Become less random over time)
    if epsilon > 0.1:
        epsilon -= 0.02
        
    print(f"Episode {episode + 1} complete. Epsilon is now {epsilon:.1f}")

# --- RESULTS ---
print("\nTraining Complete!")
print("Final Q-Table (Cheat Sheet):")
print("   [Left, Right]")
print(q_table)


print("\n\n--- TEST RUN (AI Playing) ---")
state = 0  # Reset to start
done = False
steps = 0

print("Start at State 0")

while not done and steps < 10:
    # 1. Ask the Brain: What is the best move?
    # np.argmax picks the index with the HIGHEST value
    action = np.argmax(q_table[state])
    
    # 2. Decode action for display
    move_name = "Right" if action == 1 else "Left"
    
    # 3. Take the move (Simulating the environment again)
    if action == 1:
        next_state = state + 1
    else:
        next_state = state - 1
        
    # Boundary check
    next_state = max(0, min(next_state, STATES - 1))
    
    print(f"State {state} -> AI chooses {move_name} -> Lands in State {next_state}")
    
    # Check for win
    if next_state == 5:
        print("🎉 VICTORY! The AI navigated the maze perfectly.")
        done = True
    
    state = next_state
    steps += 1

if not done:
    print("❌ The AI got lost or ran out of steps.")