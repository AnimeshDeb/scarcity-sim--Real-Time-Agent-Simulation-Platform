import random

# --- CONFIGURATION ---
GRID_SIZE = 10
GLOBAL_START_MONEY = 1000  # The Shared Public Pot
START_HUNGER = 100
FOOD_COST = 50 
SHOP_X = GRID_SIZE // 2
SHOP_Y = GRID_SIZE // 2

def create_agent(id):
    return {
        "id": id,
        "x": random.randint(0, GRID_SIZE - 1),
        "y": random.randint(0, GRID_SIZE - 1),
        "hunger": START_HUNGER,
        "is_alive": True
        # Note: No individual 'money' variable anymore
    }

def init_game_state():
    return {
        "money": GLOBAL_START_MONEY,
        "agents": [create_agent(i) for i in range(10)]
    }

def move_agent(agent):
    if not agent["is_alive"]: return agent
    new_agent = agent.copy()
    
    # Random Move
    dx, dy = random.choice([(0,1), (0,-1), (1,0), (-1,0)])
    new_x = new_agent["x"] + dx
    new_y = new_agent["y"] + dy
    
    if 0 <= new_x < GRID_SIZE: new_agent["x"] = new_x
    if 0 <= new_y < GRID_SIZE: new_agent["y"] = new_y
    
    new_agent["hunger"] -= 1
    return new_agent

def resolve_interactions(agent, current_global_money):
    """
    Returns a tuple: (Updated Agent, Cost Incurred)
    """
    if not agent["is_alive"]: return agent, 0
    
    new_agent = agent.copy()
    cost = 0

    # Rule 1: Starvation
    if new_agent["hunger"] <= 0:
        new_agent["is_alive"] = False
        return new_agent, 0

    # Rule 2: Shop Interaction (Shared Budget)
    if new_agent["x"] == SHOP_X and new_agent["y"] == SHOP_Y:
        # Check if the PUBLIC POT has enough money
        if current_global_money >= FOOD_COST and new_agent["hunger"] < 90:
            cost = FOOD_COST
            new_agent["hunger"] = 100
            
    return new_agent, cost

def run_simulation_step(current_state):
    """
    Updates the entire world, including the shared money pot.
    """
    agents = current_state["agents"]
    money = current_state["money"]
    
    next_agents = []
    
    for agent in agents:
        # 1. Move
        moved_agent = move_agent(agent)
        
        # 2. Interact (Pass current money to see if they can afford it)
        final_agent, cost = resolve_interactions(moved_agent, money)
        
        # 3. Deduct Cost from Global Pot immediately
        money -= cost
        next_agents.append(final_agent)
        
    return {
        "money": money,
        "agents": next_agents
    }