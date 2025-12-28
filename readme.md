An interactive full-stack dashboard utilizing React and Python to visualize, tune, and analyze reinforcement learning agents solving resource optimization problems.  

2 problems that were faced:
- Ai didn't know the apples were gone so it thought a previous square still had an apple, this forced the ai to go back and forth between two squares. -> implemented a q table during the replay phase which took into account apple consumation with rewards

- During replay, the ai still got stuck in a loop because previous square had a better value (score) than current and so on. -> Implemented higher penalty during replay phase to force ai to move elsewhere instead of waiting